def get_xblock_parent(xblock, category=None):
    parent = xblock.get_parent()
    if parent and category:
        if parent.category == category:
            return parent
        else:
            return get_xblock_parent(parent, category)
    return parent
