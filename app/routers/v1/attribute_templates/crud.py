from uuid import UUID

from fastapi_sqlalchemy import db

from app.models.base_models import APIResponse
from app.models.models_attribute_templates import DELETETemplate
from app.models.models_attribute_templates import GETTemplate
from app.models.models_attribute_templates import POSTTemplate
from app.models.models_attribute_templates import PUTTemplate
from app.models.sql_attribute_templates import AttributeTemplateModel
from app.routers.router_utils import paginate


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
