from haystack.backends.solr_backend import SolrSearchBackend, SolrEngine
from haystack.exceptions import MissingDependency

try:
    from pysolr import Solr, SolrError
except ImportError:
    raise MissingDependency(
        "The 'solr' backend requires the installation of 'pysolr'. Please refer to the documentation."
    )


class CustomSolrSearchBackend(SolrSearchBackend):

    def build_schema(self, fields):
        content_field_name = ""
        schema_fields = []

        for field_name, field_class in fields.items():
            field_data = {
                "name": field_class.index_fieldname,
                "type": field_class.field_type,
                "indexed": "true",
                "stored": "true",
                "multiValued": "false",
            }

            if field_class.document is True:
                content_field_name = field_class.index_fieldname

            # DRL_FIXME: Perhaps move to something where, if none of these
            #            checks succeed, call a custom method on the form that
            #            returns, per-backend, the right type of storage?
            if field_class.field_type in ["date", "datetime"]:
                field_data["type"] = "date"
            elif field_class.field_type == "integer":
                field_data["type"] = "long"
            elif field_class.field_type == "float":
                field_data["type"] = "float"
            elif field_class.field_type == "boolean":
                field_data["type"] = "boolean"
            elif field_class.field_type == "ngram":
                field_data["type"] = "ngram"
            elif field_class.field_type == "edge_ngram":
                field_data["type"] = "edge_ngram"
            elif field_class.field_type == "location":
                field_data["type"] = "location"
            elif field_class.field_type == "string":
                # setting the our field type for texts
                field_data["type"] = "text_es"

            if field_class.is_multivalued:
                field_data["multiValued"] = "true"

            if field_class.stored is False:
                field_data["stored"] = "false"

            # Do this last to override `text` fields.
            if field_class.indexed is False:
                field_data["indexed"] = "false"

                # If it's text and not being indexed, we probably don't want
                # to do the normal lowercase/tokenize/stemming/etc. dance.
                if field_data["type"] == "text_es":
                    field_data["type"] = "string"

            # If it's a ``FacetField``, make sure we don't postprocess it.
            if hasattr(field_class, "facet_for"):
                # If it's text, it ought to be a string.
                if field_data["type"] == "text_en":
                    field_data["type"] = "string"

            # joining field data with with extra_attr
            if hasattr(field_class, "extra_attr"):
                field_data = {**field_data, **field_class.extra_attr}

            schema_fields.append(field_data)

        return (content_field_name, schema_fields)


class CustomSolrEngine(SolrEngine):
    backend = CustomSolrSearchBackend
