from pathlib import Path

from ros2bag_tools.exporter import Exporter

class JointStatesExporter(Exporter):
    """Centroid .json files per scene_update message."""

    def __init__(self):
        self._dir = None
        self._name = None
        self._i = 0

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

    def write(self, topic, joint_state, t):
        tpc_path = topic.lstrip('/').replace('/', '_')
        filename = self._name.replace('%tpc', tpc_path)
        filename = filename.replace('%t', str(t))
        filename = filename.replace('%i', str(self._i).zfill(8))
        joint_state_path = self._dir / filename

        with open(str(joint_state_path), 'w') as f:

            f.write('{\n')
            f.write('    "header": {\n')
            f.write('        "stamp": {\n')
            f.write(f'            "sec": {joint_state.header.stamp.sec},\n')
            f.write(f'            "nanosec": {joint_state.header.stamp.nanosec}\n')
            f.write('        },\n')
            f.write(f'        "frame_id": "{joint_state.header.frame_id}"\n')
            f.write('    },\n')
            
            # write the objects
            joints = [joint for joint in joint_state.name]
            f.write('    "position": {\n')
            for i, joint in enumerate(joints):
                if i == len(joints)-1:
                    f.write(f'        "{joint}": {joint_state.position[i]}\n')
                else:
                    f.write(f'        "{joint}": {joint_state.position[i]},\n')
            f.write('    },\n')
            f.write('    "velocity": {\n')
            for i, joint in enumerate(joints):
                if i == len(joints)-1:
                    f.write(f'        "{joint}": {joint_state.velocity[i]}\n')
                else:
                    f.write(f'        "{joint}": {joint_state.velocity[i]},\n')
            f.write('    },\n')
            f.write('    "effort": {\n')
            for i, joint in enumerate(joints):
                if i == len(joints)-1:
                    f.write(f'        "{joint}": {joint_state.effort[i]}\n')
                else:
                    f.write(f'        "{joint}": {joint_state.effort[i]},\n')
            f.write('    }\n')
            f.write('}\n')
