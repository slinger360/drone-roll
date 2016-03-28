import struct

data_types = {
    'ack': 1,
    'data': 2,
    'low_latency_data': 3,
    'data_with_ack': 4
}
data_type_names = {v:k for k, v in data_types.items()}

characteristic_ids = {
    'non_ack': 'fa0a',
    'ack': 'fa0b',
    'emergency': 'fa0c',
    'battery': 'fb0f'
}


# list is not complete
projects = {
    'common': {
        'project_id': 0,
        'classes': {
            'CommonState': {
                'class_id': 5,
                'commands': (
                    "AllStatesChanged", "BatteryStateChanged",
                    "MassStorageStateListChanged", "MassStorageInfoStateListChanged",
                    "CurrentDateChanged", "CurrentTimeChanged",
                    "MassStorageInfoRemainingListChanged", "WifiSignalChanged",
                    "SensorsStatesListChanged", "ProductModel",
                    "CountryListKnown"
                )
            }
        },
    },
    'mini_drone': {
        'project_id': 2,
        'classes': {
            'Piloting': {
                'class_id': 0,
                'commands': (
                    'FlatTrim', 'TakeOff',
                    'PCMD', 'Landing',
                    'Emergency', 'AutoTakeOffMode')
            },
            "SpeedSettings": {
                'class_id': 1,
                'commands': (
                    'MaxVerticalSpeed', 'MaxRotationSpeed',
                    'Wheels', 'MaxHorizontalSpeed',
                )
            },
        }
    },
}

project_names = {v['project_id']:k for k,v in projects.items()}
command_classes_names = {(v['project_id'], vv['class_id']):kk
                         for k,v in projects.items()
                         for kk,vv in v['classes'].items()}
command_names = {(v['project_id'], vv['class_id'], vv['commands'].index(cmd)):cmd
                 for k,v in projects.items()
                 for kk,vv in v['classes'].items()
                 for cmd in vv['commands']}

UPDATE_NOTIFICATION_DESCRIPTOR_UUID = "00002902-0000-1000-8000-00805f9b34fb"

class Packet(object):
    """Network packet packer/unpacker
    Packet format:
           |data type|sequence_number|project ID|command class ID|command ID|command arguments...|
    Sizes:  1 byte    1byte           1 byte     1 byte           2 bytes    differ

    >>> Packet.unpack([2, 1, 2, 0, 4, 0])
    <Packet DT:2(data) SQ:1 PJ:2(mini_drone) CL:0(Piloting) CC:4(Emergency) args:[]>
    >>> Packet.unpack([2, 3, 2, 1, 2, 0, 1])
    <Packet DT:2(data) SQ:3 PJ:2(mini_drone) CL:1(SpeedSettings) CC:2(Wheels) args:[1]>
    >>> Packet(data_type=2, sequence_number=3, project_id=0,
    ... class_id=5, command_id=1, arguments=[95]).pack()
    [2, 3, 0, 5, 1, 0, 95]
    """

    fmt = '<Packet DT:{DT}({dt}) SQ:{SQ} PJ:{PJ}({pj}) CL:{CL}({cl}) CC:{CC}({cc}) args:{args}>'

    def __init__(self, data_type, sequence_number, project_id, class_id, command_id, arguments):
        self.data_type = data_type
        self.sequence_number = sequence_number
        self.project_id = project_id
        self.class_id = class_id
        self.command_id = command_id
        self.arguments = arguments or []

    def __repr__(self):
        cl = command_classes_names.get((self.project_id, self.class_id), '??')
        cc = command_names.get((self.project_id, self.class_id, self.command_id), '??')
        return self.fmt.format(
            DT=self.data_type, dt=data_type_names.get(self.data_type, '??'),
            SQ=self.sequence_number,
            PJ=self.project_id, pj=project_names.get(self.project_id, '??'),
            CL=self.class_id, cl=cl,
            CC=self.command_id, cc=cc,
            args=list(self.arguments)
        )

    def pack(self):
        return  [self.data_type, self.sequence_number,
                 self.project_id,self. class_id,
                 self.command_id,
                 0 # command ID second byte
        ] + self.arguments

    @classmethod
    def unpack(self, data):
        unpacked = struct.unpack_from('<BBBBH', buffer(bytearray(data)))
        arguments = data[6:]
        return Packet(*unpacked+(arguments,))