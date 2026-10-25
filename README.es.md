# Web de Coverly Shelf

[English](README.md)

La web de [Coverly Shelf](https://github.com/MAECLY/coverly-shelf), publicada en
**https://coverly-shelf.maecly.com**: una página estática y bilingüe (español en
`/`, inglés en `/en/`) sin framework, sin dependencias y sin rastreadores. La
extensión, sus versiones y sus incidencias están en
[MAECLY/coverly-shelf](https://github.com/MAECLY/coverly-shelf).

Coverly Shelf es una extensión de navegador puramente cosmética que añade la
portada en una caja 3D hecha con CSS y una galería de capturas a las fichas de
juegos de 3DS en hShop. Forma parte de la familia Coverly, junto a
[Coverly ROMs](https://coverly-roms.maecly.com), y comparte sus tokens de diseño
y sus fuentes.

## Probarla en local

Necesitas `python3` y `node` (24 o posterior); no hay nada que instalar.

```bash
make site                  # compila y sirve en http://localhost:8080
make site SITE_PORT=8111   # otro puerto
make check                 # todas las comprobaciones, igual que en Vercel
make help                  # todos los objetivos
```

`make check` comprueba que los tokens están al día y cumplen el contraste, y
ejecuta `scripts/site/check_site.py` (archivos necesarios, enlaces y anclas,
paridad español/inglés, cabeceras y CSP, nada de código de terceros ni
rastreadores, y límites de tamaño).

## Cómo se publica

Integración de Vercel con Git: cada push a `main` publica en producción y las
pull requests tienen vista previa. `vercel.json` ejecuta
`scripts/site/vercel_build.sh`, que pasa las comprobaciones y copia `site/` a
`target/site`, la carpeta que sirve Vercel. El dominio
`coverly-shelf.maecly.com` es un CNAME sin proxy en la zona `maecly.com` de
Cloudflare que apunta a Vercel.

## Licencia

[AGPL-3.0](LICENSE), como la extensión. Las fuentes usan la SIL Open Font
License 1.1; consulta [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md).
