from cuentas.permissions import (
    dashboard_permissions,
    get_role_names,
    is_administrator,
    is_guide_operator,
    is_tourist_client,
)


def role_context(request):
    user = request.user
    if not user.is_authenticated:
        return {
            'permissions': {
                'administrador': 0,
                'guia': 0,
                'operador': 0,
                'turista': 0,
                'cliente': 0,
            },
            'roles': [],
            'is_administrator': False,
            'is_guide_operator': False,
            'is_tourist_client': False,
        }

    return {
        'permissions': dashboard_permissions(user),
        'roles': get_role_names(user),
        'is_administrator': is_administrator(user),
        'is_guide_operator': is_guide_operator(user),
        'is_tourist_client': is_tourist_client(user),
    }
