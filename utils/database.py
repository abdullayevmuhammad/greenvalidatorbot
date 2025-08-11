from django.db import transaction
from server.application.models import Applicant, Dependent

async def save_application(data: dict):
    with transaction.atomic():
        applicant = Applicant.objects.create(
            full_name=data['full_name'],
            address=data['address'],
            email=data['email'],
            children_count=data['children_count'],
            phone_number=data['phone']
        )
        
        if data['marital_status'] == 'married':
            Dependent.objects.create(
                applicant=applicant,
                full_name=data['wife_full_name'],
                status='wife'
            )
        
        for i in range(data['children_count']):
            Dependent.objects.create(
                applicant=applicant,
                full_name=data[f'child_{i}_name'],
                status='child'
            )
    return applicant