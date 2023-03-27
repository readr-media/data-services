from draftjs_exporter.constants import BLOCK_TYPES, ENTITY_TYPES, INLINE_STYLES
from draftjs_exporter.defaults import BLOCK_MAP, STYLE_MAP
from draftjs_exporter.dom import DOM
from draftjs_exporter.html import HTML


def image(props):
    # This component creates an image element, with the relevant attributes.
    figure = DOM.create_element('figure', {'class': 'image'})
    try:
        img = DOM.create_element('img', {'src': props.get('resized').get('original'),
                                         'alt': props.get('desc')})
    except AttributeError:
        img = DOM.create_element('img', {'src': props.get('src'),
                                         'alt': props.get('desc')})
    figcaption = DOM.create_element(
        'figcaption', {'class': 'image'}, props.get('desc'))
    DOM.append_child(figure, img)
    DOM.append_child(figure, figcaption)
    return figure


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


def colorbox(props):
    return DOM.create_element('div', {
        'color': props.get('color')
    }, props["children"])


def entity_fallback(props):
    return DOM.create_element(
        "span", {"class": "missing-entity"}, props["children"]
    )


def style_fallback(props):
    return props["children"]


config = {
    "block_map": dict(
        BLOCK_MAP,
        **{
            '': None
        }
    ),
    'entity_decorators': {
        'image': image,
        "IMAGE": image,
        ENTITY_TYPES.LINK: link,
        "EMBEDDEDCODE": embeddedcode,
        "DIVIDER": divider,
        "COLORBOX": colorbox,
        ENTITY_TYPES.FALLBACK: entity_fallback,

    },
    "style_map": dict(
        STYLE_MAP,
        **{
            # Provide a fallback component (advanced).
            INLINE_STYLES.FALLBACK: style_fallback,
        },
    )
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
