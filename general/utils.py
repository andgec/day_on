def get_fields_visible(company):
    cfg = company.get_config_value('TIMEREG_TASK_MODE')
    fields_visible = {
        'item': cfg == '1000',
        'description': cfg == '2000',
    }
    return fields_visible
