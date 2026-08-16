from extract import extract, salvar_raw, CIDADES

if __name__ == "__main__":
    resultados = []
    for cidade in CIDADES:
        dado = extract(cidade)
        if dado is not None:
            resultados.append(dado)

    if resultados:
        salvar_raw(resultados, "clima")