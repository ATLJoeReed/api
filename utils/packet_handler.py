from config import constants # noqa


class PacketHandler(object): # noqa
    """This is the packet handler class for the cstore request packets.
    """
    def __init__(self, request, validation_type): # noqa
        """
        Args:
        __request__: Request packet requesting an action from cstore.
        __logger__: Logger
        """
        self.request = request
        self.validation_type = validation_type


    def is_valid(self): # noqa
        """Simple request packet validation. Just looking at the top level
        elements.

        Returns:
        True if valid, False if not.
        """
        if not constants.VALID_PACKET_ELEMENTS.get(self.validation_type, None):
            return False

        for element in \
                constants.VALID_PACKET_ELEMENTS.get(self.validation_type, []):
            if element not in self.request:
                return False

        if len(self.request) != \
                len(constants.VALID_PACKET_ELEMENTS.get(self.validation_type)):
            return False

        if self.validation_type == 'create_user':
            if self.request['request_type'] \
                    not in ['gift_card_redeemer', 'join_existing_user']:
                return False

        return True
