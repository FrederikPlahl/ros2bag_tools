from pathlib import Path
from ros2bag_tools.exporter import Exporter

class Labels2DExporter(Exporter):
    """Label .json files per image label message."""

    def __init__(self):
        self._dir = None
        self._name = None
        self._i = 0
        self.written_once = False

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--dir', default='.', help='Output directory')
        parser.add_argument('--name', default='%t.json',
                            help="""Filename pattern of output label files.
                            Placeholders:
                                %%tpc ... topic
                                %%t   ... timestamp
                                %%i   ... sequence index""")

    def open(self, args):  # noqa: A003
        self._dir = Path(args.dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._name = args.name
        self._i = 0

    def write(self, topic, label, t):
        # print(f'msg: {label} at time {t}')
        tpc_path = topic.lstrip('/').replace('/', '_')
        filename = self._name.replace('%tpc', tpc_path)
        filename = filename.replace('%t', str(t))
        filename = filename.replace('%i', str(self._i).zfill(8))
        label_path = self._dir / filename
        id = filename.split('.')[0]

        # {
        #     "annotations": [
        #         {
        #         "id": 1,
        #         "image_id": 1,
        #         "category_id": 1,
        #         "keypoints": [100, 200, 2, 110, 220, 2, ...],  // Keypoints for image 1
        #         "num_keypoints": 17,
        #         "bbox": [60, 200, 120, 600],
        #         "iscrowd": 0
        #         },
        #         {
        #         "id": 2,
        #         "image_id": 2,
        #         "category_id": 1,
        #         "keypoints": [120, 210, 2, 115, 225, 2, ...],  // Keypoints for image 2
        #         "num_keypoints": 17,
        #         "bbox": [65, 210, 110, 590],
        #         "iscrowd": 0
        #         }
        #         // ...more annotations
        #     ],
        # }
        
        with open(str(label_path), 'w') as f:
            keypoint_instances = [keypoint_instance for keypoint_instance in label.instances]

            f.write('{\n')
            f.write(f'    "annotations": [\n')
            # write the annotations
            for i, keypoint_instance in enumerate(keypoint_instances):
                if label.fields[i] == "human":
                    category_id = 1
                elif label.fields[i] == "robot":
                    category_id = 2
                f.write('        {\n')
                f.write(f'        "id": {id},\n')
                f.write(f'        "image_id": {id},\n')
                f.write(f'        "category_id": {category_id},\n')
                f.write(f'        "keypoints": [')
                for j, keypoint_array in enumerate(keypoint_instance.keypoints):
                    for keypoint in keypoint_array.keypoint:
                        f.write(f'{keypoint.u}, {keypoint.v}, {keypoint.confidence}')
                        if j != len(keypoint_instance.keypoints)-1:
                            f.write(', ')
                f.write('],\n')
                f.write(f'        "num_keypoints": {len(keypoint_instance.keypoints)},\n')
                f.write(f'        "iscrowd": 0\n')
                if i == len(keypoint_instances)-1:
                    f.write('        }\n')
                else:
                    f.write('        },\n')
            f.write('    ]\n')
            f.write('}')
        
        # {
        #   "categories": [
        #       {
        #       "id": 1,
        #       "name": "person",
        #       "keypoints": ["nose", "left_eye", "right_eye", "left_ear", ...]
        #       }
        #   ]
        # }

        if not self.written_once:
            category_path = self._dir / 'categories.json'
            with open(str(category_path), 'w') as f:
                f.write('{\n')
                f.write('    "categories": [\n')
                f.write('        {\n')
                f.write('        "id": 1,\n')
                f.write('        "name": "human",\n')
                f.write('        "keypoints": ["nose", "left_eye", "right_eye", "left_ear", "right_ear", "left_shoulder", "right_shoulder", "left_elbow", "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"]\n')
                f.write('        },\n')
                f.write('        {\n')
                f.write('        "id": 2,\n')
                f.write('        "name": "robot",\n')
                f.write('        "keypoints": ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link", "wrist_3_link", "robotiq_arg2f_base_link"]\n')
                f.write('        }\n')
                f.write('    ]\n')
                f.write('}')
            self.written_once = True
