from db import buscar_configs, salvar_configs

print("Buscando configs atuais...")
cfg = buscar_configs()
print(cfg)

print("Salvando novos valores (10, 25)...")
salvar_configs(10, 25)

print("Buscando novamente...")
cfg = buscar_configs()
print(cfg)
