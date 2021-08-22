"""Common implementation of UDS packets for all bus types."""

__all__ = ["AbstractPacketType", "AbstractUdsPacket", "AbstractUdsPacketRecord"]

from abc import ABC, abstractmethod
from typing import Any

from uds.utilities import NibbleEnum, ValidatedEnum, ExtendableEnum, \
    RawByte, RawBytes, RawBytesTuple, validate_raw_bytes,\
    ReassignmentError, TimeStamp
from .transmission_attributes import AddressingMemberTyping, AddressingType, \
    TransmissionDirection, DirectionMemberTyping


class AbstractPacketType(NibbleEnum, ValidatedEnum, ExtendableEnum):  # pylint: disable=too-many-ancestors
    """
    Abstract definition of UDS packet type.

    Packet type information is carried by Network Protocol Control Information (N_PCI).
    Enums with packet types (N_PCI) values for certain buses (e.g. CAN, LIN, FlexRay) must inherit after this class.

    Note: There are some differences in values for each bus (e.g. LIN does not use Flow Control).
    """


class AbstractUdsPacket(ABC):
    """Abstract definition of UDS Packet (Network Protocol Data Unit - N_PDU )."""

    def __init__(self, raw_data: RawBytes, addressing: AddressingMemberTyping) -> None:
        """
        Create a storage for a single UDS packet.

        :param raw_data: Raw bytes of UDS packet data.
        :param addressing: Addressing type for which this packet is relevant.
        """
        self.raw_data = raw_data  # type: ignore
        self.addressing = addressing  # type: ignore

    @property
    def raw_data(self) -> RawBytesTuple:
        """Raw bytes of data that this packet carries."""
        return self.__raw_data

    @raw_data.setter
    def raw_data(self, value: RawBytes):
        """
        Set value of raw bytes of data.

        :param value: Raw bytes of data to be carried by this packet.
        """
        validate_raw_bytes(value)
        self.__raw_data = tuple(value)

    @property
    def addressing(self) -> AddressingType:
        """Addressing type for which this packet is relevant."""
        return self.__addressing

    @addressing.setter
    def addressing(self, value: AddressingMemberTyping):
        """
        Set value of addressing type attribute.

        :param value: Value of addressing type to set.
        """
        AddressingType.validate_member(value)
        self.__addressing = AddressingType(value)

    @property  # noqa: F841
    @abstractmethod
    def packet_type(self) -> AbstractPacketType:
        """Type of UDS packet - N_PCI value of this N_PDU."""


class AbstractUdsPacketRecord(ABC):
    """Abstract definition of a record that stores historic information about transmitted or received UDS packet."""

    @abstractmethod
    def __init__(self, frame: object, direction: DirectionMemberTyping) -> None:
        """
        Create historic record of a packet that was either received of transmitted to a bus.

        :param frame: Frame that carried this UDS packet.
        :param direction: Information whether this packet was transmitted or received.
        """
        self.frame = frame
        self.direction = direction  # type: ignore

    @abstractmethod
    def __validate_frame(self, value: Any) -> None:
        """
        Validate value of a frame before attribute assignment.

        :param value: Frame value to validate.

        :raise TypeError: Frame has other type than expected.
        :raise ValueError: Some values of a frame are not
        """

    def __get_raw_packet_type(self) -> RawByte:
        """
        Get raw value of packet type (N_PCI).

        :return: Integer value of N_PCI.
        """
        return (self.raw_data[0] >> 4) & 0xF  # TODO: make sure it is the first nibble of data for all buses

    @property
    def frame(self) -> object:
        """Frame that carried this packet."""
        return self.__frame

    @frame.setter
    def frame(self, value: DirectionMemberTyping):
        """
        Set value of frame attribute.

        :param value: Frame value to set.

        :raise ReassignmentError: There is a call to change the value after the initial assignment (in __init__).
        """
        try:
            self.__getattribute__("_AbstractUdsPacketRecord__frame")
        except AttributeError:
            self.__validate_frame(value)
            self.__frame = value
        else:
            raise ReassignmentError("You cannot change value of 'frame' attribute once it is assigned.")

    @property
    def direction(self) -> TransmissionDirection:
        """Information whether this packet was transmitted or received."""
        return self.__direction

    @direction.setter
    def direction(self, value: DirectionMemberTyping):
        """
        Set value of direction attribute.

        :param value: Direction value to set.

        :raise ReassignmentError: There is a call to change the value after the initial assignment (in __init__).
        """
        try:
            self.__getattribute__("_AbstractUdsPacketRecord__direction")
        except AttributeError:
            TransmissionDirection.validate_member(value)
            self.__direction = TransmissionDirection(value)
        else:
            raise ReassignmentError("You cannot change value of 'direction' attribute once it is assigned.")

    @property
    @abstractmethod
    def raw_data(self) -> RawBytesTuple:
        """Raw bytes of data that this N_PDU carried."""

    @property   # noqa: F841
    @abstractmethod
    def packet_type(self) -> AbstractPacketType:
        """Type of UDS packet - N_PCI value carried by this N_PDU."""

    @property
    @abstractmethod
    def addressing(self) -> AddressingType:
        """Addressing type over which this packet was transmitted."""

    @property  # noqa: F841
    @abstractmethod
    def transmission_time(self) -> TimeStamp:
        """Time stamp when this packet was fully transmitted on a bus."""