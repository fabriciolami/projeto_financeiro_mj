PERMISSIONS = {
    "MASTER": {
        "funcionario_criar": True,
        "funcionario_editar": True,
        "funcionario_excluir": True,
        "marcar_pagamento": True,
        "excluir_pagamento": True,
    },
    "FINANCEIRO": {
        "funcionario_criar": False,
        "funcionario_editar": False,
        "funcionario_excluir": False,
        "marcar_pagamento": False,
        "excluir_pagamento": False,
    }
}

def has_permission(perfil, permissao):
    perfil = perfil.upper()
    if perfil == "MASTER":
        return True  # 🔥 master sempre pode tudo
    return PERMISSIONS.get(perfil, {}).get(permissao, False)
