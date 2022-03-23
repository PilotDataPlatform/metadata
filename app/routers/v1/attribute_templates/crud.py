from uuid import UUID

from fastapi_sqlalchemy import db

from app.models.base_models import APIResponse
from app.models.models_attribute_templates import DELETETemplate
from app.models.models_attribute_templates import GETTemplate
from app.models.models_attribute_templates import GETTemplates
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import PUTTemplate
from app.models.sql_attribute_templates import AttributeTemplateModel
from app.routers.router_utils import paginate


def get_template_by_id(params: GETTemplate, api_response: APIResponse):
    template_query = db.session.query(AttributeTemplateModel).filter_by(id=params.id)
    api_response.result = template_query.first().to_dict()


def get_templates_by_project_id(params: GETTemplates, api_response: APIResponse):
    template_query = db.session.query(AttributeTemplateModel).filter_by(project_id=params.project_id)
    paginate(params, api_response, template_query, None)


def create_template(data: POSTTemplate, api_response: APIResponse):
    json_attributes = []
    for attribute in data.attributes:
        json_attributes.append(
            {
                'name': attribute.name,
                'optional': attribute.optional,
                'type': attribute.type.value,
                'value': attribute.value,
            }
        )
    template_model_data = {
        'name': data.name,
        'project_id': data.project_id,
        'attributes': json_attributes,
    }
    template = AttributeTemplateModel(**template_model_data)
    db.session.add(template)
    db.session.commit()
    db.session.refresh(template)
    api_response.result = template.to_dict()


def update_template(template_id: UUID, data: PUTTemplate, api_response: APIResponse):
    template = db.session.query(AttributeTemplateModel).filter_by(id=template_id).first()
    template.name = data.name
    template.project_id = data.project_id
    template.attributes = data.attributes
    db.session.commit()
    db.session.refresh(template)
    api_response.result = template.to_dict()


def delete_template_by_id(params: DELETETemplate, api_response: APIResponse):
    template_query = db.session.query(AttributeTemplateModel).filter_by(id=params.id)
    db.session.delete(template_query.first())
    db.session.commit()
    api_response.total = 0
    api_response.num_of_pages = 0
