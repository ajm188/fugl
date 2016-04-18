def parse_markdown(md):
    idx = md.find('\n\n')
    prefix = md[:idx]
    suffix = md[idx+2:]
    pairs = [l.split(':', maxsplit=1) for l in prefix.splitlines()]
    pairs = [(fst.strip(), snd.strip()) for fst, snd in pairs]
    frontmatter = dict(pairs)
    return frontmatter, suffix[:-1]
