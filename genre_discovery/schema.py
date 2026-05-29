import graphene
from cloudcasts.schema import Query as CloudcastQuery

class Query(CloudcastQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
