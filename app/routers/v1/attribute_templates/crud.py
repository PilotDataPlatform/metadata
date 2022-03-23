from fastapi_sqlalchemy import db

from app.models.base_models import APIResponse
from app.models.models_attribute_templates import DELETETemplate
from app.models.models_attribute_templates import GETTemplate
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import PUTTemplate
from app.models.sql_attribute_templates import AttributeTemplateModel


def create_template(data: POSTTemplate, api_response: APIResponse):
    template_model_data = {
        'name': data.name,
        'project_id': data.project_id,
        'attributes': data.attributes,
    }
    template = AttributeTemplateModel(**template_model_data)
    db.session.add(template)
    db.session.commit()
    db.session.refresh(template)
    api_response.result = template.to_dict()


def delete_template_by_id(params: DELETETemplate, api_response: APIResponse):
    template_query = db.session.query(AttributeTemplateModel).filter_by(id=params.id)
    db.session.delete(template_query.first())
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0
