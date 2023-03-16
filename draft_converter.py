from draftjs_exporter.constants import BLOCK_TYPES, ENTITY_TYPES
from draftjs_exporter.defaults import BLOCK_MAP, STYLE_MAP
from draftjs_exporter.dom import DOM
from draftjs_exporter.html import HTML


def image(props):
    # This component creates an image element, with the relevant attributes.
    try:
        return DOM.create_element('img', {
            'src': props.get('resized').get('original'),
            'alt': props.get('desc'),
        })
    except AttributeError:
        return DOM.create_element('img', {
            'src': props.get('src'),
            'alt': props.get('desc'),
        })


def link(props):
    return DOM.create_element('a', {
        'href': props.get('url')
    }, props["children"])


def embeddedcode(props):
    return DOM.create_element('iframe', {
        'src': props.get('embeddedCode')
    }, props["children"])


def divider(props):
    return DOM.create_element("hr")


config = {
    "block_map": dict(
        BLOCK_MAP,
        **{
            '': None
        }
    ),
    'entity_decorators': {
        'image': image,
        ENTITY_TYPES.LINK: link,
        'EMBEDDEDCODE': embeddedcode,
        'DIVIDER': divider,
        'ANNOTATION'
        'TABLE': None,
        '': None
    },
}


def convert_draft_to_html(draft):
    # Initialise the exporter.
    exporter = HTML(config)

    # Render a Draft.js `contentState`
    html = exporter.render(draft)
    # print(html)
    return html


if __name__ == '__main__':
    draft = {}
    convert_draft_to_html(draft)
