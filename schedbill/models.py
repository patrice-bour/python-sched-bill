from uuid import uuid1, uuid4
import json


class Base():
    """"""

    @staticmethod
    def get_uuid() -> str:
        """Static method. Generate a random uuid.
        :return: the unique identifier generated
        """

        return str(uuid4())

    def __init__(self, uuid: str = None):
        """Constructor.
        :param uuid: the uuid in case of an existing user
        """

        self._uuid = uuid

    @property
    def uuid(self) -> str:
        """Retrieve the object's uuid.
        :return: the object uuid
        """

        return self._uuid


class User(Base):
    """Represent a user identified by an uuid and an email address.
    """

    def __init__(self, uuid: str = None, email: str = None):
        """Constructor.
        :param uuid: the uuid in case of an existing user
        :param email: the email of the user
        """

        super().__init__(uuid=uuid)
        self._uuid = uuid
        self._email = email

    @property
    def email(self) -> str:
        """Retrieve the user's email address.
        :return: the user's email address
        """

        return self._email

    @email.setter
    def email(self, value: str):
        """Set the user email address.
        :param value: the email address
        """

        self._email = value

    def to_string(self) -> str:
        """Serialize the object as a string
        :return: the string representing the object's value
        """

        return f"{self.email} ({self.uuid})"

    def to_json(self) -> str:
        """Serialize the object as a JSON string
        :return: the JSON mapping of the object with sorted keys
        """

        return json.dumps({
            'email': self.email,
            'uuid': self.uuid
        }, sort_keys=True)
