from pathlib import Path

import math

from ros2bag_tools.exporter import Exporter

def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return math.degrees(roll_x), math.degrees(pitch_y), math.degrees(yaw_z) # in degrees

class LabelsExporter(Exporter):
    """Centroid .json files per scene_update message."""

    def __init__(self):
        self._dir = None
        self._name = None
        self._i = 0

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

        with open(str(label_path), 'w') as f:
            folder = str(self._dir)
            pcd_file = str(filename) # TODO: change this to the pcd filename
            path = str(label_path) # TODO: change this to the pcd path
            entities = [entity for entity in label.entities]

            f.write('{\n')
            f.write(f'    "folder": "{folder}",\n')
            f.write(f'    "filename": "{pcd_file}",\n')
            f.write(f'    "path": "{path}",\n')
            f.write(f'    "objects": [\n')
            # write the objects
            for i, entity in enumerate(entities):
                label_id = entity.id
                if entity.cubes!=None:
                    for cube in entity.cubes:
                        f.write('        {\n')
                        f.write(f'            "name": "{label_id}",\n')
                        f.write('            "centroid": {\n')
                        f.write(f'                "x": {cube.pose.position.x},\n')
                        f.write(f'                "y": {cube.pose.position.y},\n')
                        f.write(f'                "z": {cube.pose.position.z}\n')
                        f.write('            },\n')
                        f.write('            "dimensions": {\n')
                        f.write(f'                "length": {cube.size.x},\n')
                        f.write(f'                "width": {cube.size.y},\n')
                        f.write(f'                "height": {cube.size.z}\n')
                        f.write('            },\n')
                        f.write('            "rotations": {\n')
                        rpy = euler_from_quaternion(cube.pose.orientation.x, cube.pose.orientation.y, cube.pose.orientation.z, cube.pose.orientation.w)
                        f.write(f'                "x": {rpy[0]},\n')
                        f.write(f'                "y": {rpy[1]},\n')
                        f.write(f'                "z": {rpy[2]}\n')
                        f.write('            }\n')
                        if i == len(entities)-1:
                            f.write('        }\n')
                        else:
                            f.write('        },\n')
                if entity.cylinders!=None:
                    print('You are using cylinders as bounding boxes. Consider using cubes instead.')
                    for cylinder in entity.cylinders:
                        f.write('        {\n')
                        f.write(f'            "name": "{label_id}",\n')
                        f.write('            "centroid": {\n')
                        f.write(f'                "x": {cylinder.pose.position.x},\n')
                        f.write(f'                "y": {cylinder.pose.position.y},\n')
                        f.write(f'                "z": {cylinder.pose.position.z}\n')
                        f.write('          },\n')
                        f.write('            "dimensions": {\n')
                        f.write(f'                "length": {cylinder.size.x},\n')
                        f.write(f'                "width": {cylinder.size.y},\n')
                        f.write(f'                "height": {cylinder.size.z}\n')
                        f.write('          },\n')
                        f.write('            "rotations": {\n')
                        rpy = euler_from_quaternion(cylinder.pose.orientation.x, cylinder.pose.orientation.y, cylinder.pose.orientation.z, cylinder.pose.orientation.w)
                        f.write(f'                "x": {rpy[0]},\n')
                        f.write(f'                "y": {rpy[1]},\n')
                        f.write(f'                "z": {rpy[2]}\n')
                        f.write('            }\n')
                        if i == len(entities)-1:
                            f.write('        }\n')
                        else:
                            f.write('        },\n')
            f.write('    ]\n')
            f.write('}')
