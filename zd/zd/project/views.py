# project/views.py
# Перенаправляем все view функции из main.views

from main.views import (
    project_list, project_create, project_detail, project_edit,
    project_delete, project_change_status, invite_to_project,
    respond_to_invitation, cancel_invitation, remove_participant,
    add_comment, upload_file, delete_file
)

# Если нужны дополнительные view специфичные для project, добавьте их здесь
