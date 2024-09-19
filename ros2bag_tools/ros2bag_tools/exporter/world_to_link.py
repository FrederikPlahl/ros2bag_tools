from pathlib import Path

from ros2bag_tools.exporter import Exporter

class WorldToLinkExporter(Exporter):
    """One .json file containing the transformation to world of the topic."""

    def __init__(self):
        self._dir = None
        self._name = None
        self._i = 0
        self.written_once = False

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('--dir', default='.', help='Output directory')
        parser.add_argument('--name', default='%t.json',
                            help="""Filename pattern of output joint_state files.
                            Placeholders:
                                %%tpc ... topic
                                %%t   ... timestamp
                                %%i   ... sequence index""")

    def open(self, args):  # noqa: A003
        self._dir = Path(args.dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._name = args.name
        self._i = 0

    def write(self, topic, transform, t):
        tpc_path = topic.lstrip('/').replace('/', '_')
        filename = "world_to_link.json"
        transform_path = self._dir / filename

        if not self.written_once:
            with open(str(transform_path), 'w') as f:
                f.write('{\n')
                f.write(f'    "frame_id": "{transform.header.frame_id}",\n')
                f.write(f'    "child_frame_id": "{transform.child_frame_id}",\n')
                f.write('    "transform": {\n')
                f.write('        "translation": {\n')
                f.write(f'            "x": {transform.transform.translation.x},\n')
                f.write(f'            "y": {transform.transform.translation.y},\n')
                f.write(f'            "z": {transform.transform.translation.z}\n')
                f.write('        },\n')
                f.write('        "rotation": {\n')
                f.write(f'            "x": {transform.transform.rotation.x},\n')
                f.write(f'            "y": {transform.transform.rotation.y},\n')
                f.write(f'            "z": {transform.transform.rotation.z},\n')
                f.write(f'            "w": {transform.transform.rotation.w}\n')
                f.write('        }\n')
                f.write('    }\n')
            self.written_once = True
