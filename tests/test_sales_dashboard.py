from dash import dcc, html

from scripts.sales_dashboard import APP_TITLE, app


def iter_components(component):
    """Yield every component in the Dash layout tree."""
    if component is None:
        return

    yield component

    children = getattr(component, "children", None)
    if children is None:
        return
    if isinstance(children, (list, tuple)):
        for child in children:
            yield from iter_components(child)
    else:
        yield from iter_components(children)


def component_by_id(component_id: str):
    for component in iter_components(app.layout):
        if getattr(component, "id", None) == component_id:
            return component
    return None


def test_header_is_present():
    headers = [
        component
        for component in iter_components(app.layout)
        if isinstance(component, html.H1) and component.children == APP_TITLE
    ]
    assert headers, "Expected app header is missing."


def test_visualisation_is_present():
    graph = component_by_id("sales-line-chart")
    assert graph is not None, "Line chart graph component is missing."
    assert isinstance(graph, dcc.Graph)


def test_region_picker_is_present():
    region_picker = component_by_id("region-filter")
    assert region_picker is not None, "Region picker component is missing."
    assert isinstance(region_picker, dcc.RadioItems)
