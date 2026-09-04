# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/26 17:59
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: au_session_propagator.py
# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/22 16:10
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: sofa_tracer_propagator.py
import typing

from opentelemetry import trace
from opentelemetry.baggage import set_baggage
from opentelemetry.context.context import Context
from opentelemetry.propagators import textmap

from agentuniverse.base.tracing.au_trace_manager import set_session_id, \
    get_session_id
from agentuniverse.base.tracing.otel.consts import SESSION_ID_KEY, \
    HTTP_HEADER_SESSION_ID_KEY, SPAN_SESSION_ID_KEY


class AUSessionPropagator(textmap.TextMapPropagator):
    """Propagates the current session id through supported carrier keys."""

    def inject(
        self,
        carrier: textmap.CarrierT,
        context: typing.Optional[Context] = None,
        setter: textmap.Setter[textmap.CarrierT] = textmap.default_setter,
    ) -> None:
        """Inject the current session id into the carrier.

        Args:
            carrier: The carrier to inject into.
            context: The context carrying the session id.
            setter: The setter used to write the session id onto the carrier.
        """
        session_id = get_session_id()
        key_list = [
            HTTP_HEADER_SESSION_ID_KEY,
            SESSION_ID_KEY
        ]
        for _key in key_list:
            if session_id:
                setter.set(
                    carrier, _key, session_id
                )

    def extract(
        self,
        carrier: textmap.CarrierT,
        context: typing.Optional[Context] = None,
        getter: textmap.Getter[textmap.CarrierT] = textmap.default_getter,
    ) -> Context:
        """Extract the session id from the carrier into the given context.

        Args:
            carrier: The carrier to read the session id from.
            context: The context to populate with the extracted session id.
            getter: The getter used to read the session id from the carrier.

        Returns:
            The context enriched with the session id baggage.
        """
        if context is None:
            context = Context()

        key_list = [
            HTTP_HEADER_SESSION_ID_KEY,
            SESSION_ID_KEY
        ]
        for _key in key_list:
            _value = getter.get(carrier, _key)
            if _value:
                context = set_baggage(_key, _value, context)
                set_session_id(_value[0])
                span = trace.get_current_span(context)
                try:
                    span.set_attribute(SPAN_SESSION_ID_KEY, _value[0])
                except:
                    pass
                break
        return context

    @property
    def fields(self) -> typing.Set[str]:
        """Return the header keys this propagator reads and writes."""
        return {
            HTTP_HEADER_SESSION_ID_KEY,
            SESSION_ID_KEY
        }
