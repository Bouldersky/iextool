import struct
from datetime import datetime
from scapy.fields import *
from scapy.all import Packet, Raw

###########################
### Fields and utils
###########################

class IEXPriceField(LESignedLongField):
    def i2repr(self, pkt, x):
        return str(x/10000)

###########################
### IEX Transport
###########################

class MessageBlock(Packet):
    name = "messageBlock"
    fields_desc = [
        LEShortField("messageLen", None)
    ]

    def guess_payload_class(self, payload):
        if len(payload) <= 2: return Raw
        t = struct.unpack('<h', payload[:2])[0]
        if t == b'S':
            return SystemEvent

        return Raw

class IEX_TP(Packet):
    name = "IEX-TP"
    fields_desc = [
        ByteField("version", 1),
        ByteField("reserved", 0),
        LEShortField("msgProtoId", None),
        LEIntField("channelId", None),
        LEIntField("sessionId", None),
        LEFieldLenField("payloadLen", None, length_of='messages'),
        LEFieldLenField("messageCount", None, count_of='messages'),
        LESignedLongField("streamOffset", 0),
        LESignedLongField("firstSequenceNumber", 0),
        LESignedLongField("timestamp", None),
        PacketListField("messages", None, MessageBlock, count_from=lambda pkt: pkt.messageCount)
    ]

###########################
### Administrative Messages
###########################

class SystemEvent(Packet):
    _SYSTEM_EVENT_TYPES = {
        b'O': "START_OF_MESSAGES",
        b'S': "START_OF_SYSTEM_HOURS",
        b'R': "START_OF_REGULAR_MARKET_HOURS",
        b'M': "END_OF_REGULAR_MARKET_HOURS",
        b'E': "END_OF_SYSTEM_HOURS",
        b'C': "END_OF_MESSAGES"
    }

    name = "SystemEventMessage"
    fields_desc = [
        StrFixedLenField("messageType", 1, 'S'),
        ByteEnumField("systemEvent", None, _SYSTEM_EVENT_TYPES),
    ]

class SecurityDirectoryMessage(Packet):
    name = "SecurityDirectoryMessage"
    fields_desc = [
        StrFixedLenField("messageType", 1, 'D'),
        FlagsField("flags", 0, 8, {7: 'T', 6: 'W', 5: 'E'}),
        LESignedLongField("timestamp", None),
        StrFixedLenField("symbol", None, length=8),
        LEIntField("roundLotSize", None),
        IEXPriceField("adjustedPocPrice", None),
        ByteEnumField("LULDTier", None, {0:'N/A', 1:'Tier 1', 2:'Tier 2'})
    ]

class TradingStatusMessage(Packet):
    name = "TradingStatusMessage"
    fields_desc = [
        StrFixedLenField("messageType", 1, 'H'),
        FlagsField("flags", 0, 8, {7: 'F', 6: 'T', 5: 'I', 4: '8', 3: 'X'}),
    ]