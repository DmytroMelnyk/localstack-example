from pynamodb.attributes import DiscriminatorAttribute, UnicodeAttribute
from pynamodb.models import Model


# https://pynamodb.readthedocs.io/en/stable/
class UserModel(Model):
    """
    A DynamoDB User
    """

    class Meta:
        host = "http://localstack:4566"
        table_name = "dynamodb-user"

    email = UnicodeAttribute(null=True)
    first_name = UnicodeAttribute(range_key=True)
    last_name = UnicodeAttribute(hash_key=True)


class ParentModel(Model):
    class Meta:
        host = "http://localstack:4566"
        table_name = "polymorphic_table"

    id = UnicodeAttribute(hash_key=True)
    sort = UnicodeAttribute(range_key=True)
    cls = DiscriminatorAttribute()


class FooModel(ParentModel, discriminator="Foo"):
    foo = UnicodeAttribute(null=True)


class BarModel(ParentModel, discriminator="Bar"):
    bar = UnicodeAttribute(null=True)
