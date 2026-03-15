"""
Optional mDNS service advertisement for the VTN.

Advertises the VTN as a `_openadr3._tcp.local.` service so that local
clients can discover it without hardcoding URLs.

TXT record fields per the OpenADR 3.1.0 specification:
  version        — OpenADR3 version (e.g. 3.1.0)
  base_path      — URL prefix (e.g. openadr3/3.1.0)
  local_url      — Full local URL
  program_names  — Comma-separated program names
  requires_auth  — True or False
  openapi_url    — URL to the OpenAPI specification

Enabled via config.yaml:
  mdns:
    enabled: true
    service_name: OpenADR3 VTN
"""

import logging
import socket

log = logging.getLogger(__name__)

_zeroconf = None
_service_info = None

OPENADR_VERSION = '3.1.0'
BASE_PATH = f'openadr3/{OPENADR_VERSION}'


def _get_local_hostname():
    """Get the local hostname for .local URL construction."""
    hostname = socket.gethostname()
    if not hostname.endswith('.local'):
        hostname = hostname + '.local'
    return hostname


def _build_local_url(host, port):
    """Build the local_url TXT record value."""
    if host in ('0.0.0.0', '::'):
        hostname = _get_local_hostname()
    else:
        hostname = host
    scheme = 'http'
    return f'{scheme}://{hostname}:{port}/{BASE_PATH}'


def _get_program_names():
    """Fetch current program names from the object store."""
    try:
        from swagger_server.objStore.storageInterface import objStore
        programs = objStore.search_all("PROGRAM")
        if isinstance(programs, list):
            return ','.join(p.program_name for p in programs if p.program_name)
    except Exception:
        pass
    return ''


def start(host: str, port: int, service_name: str, requires_auth: bool = True):
    """Register the VTN as an mDNS service."""
    global _zeroconf, _service_info

    try:
        from zeroconf import Zeroconf, ServiceInfo
    except ImportError:
        log.warning("mdns: zeroconf package not installed — pip install zeroconf")
        return

    # Resolve the bind address to an actual IP for advertisement
    if host in ('0.0.0.0', '::'):
        addresses = None
    else:
        try:
            addresses = [socket.inet_aton(host)]
        except OSError:
            addresses = None

    service_type = "_openadr3._tcp.local."
    full_name = f"{service_name}.{service_type}"

    local_url = _build_local_url(host, port)

    # TXT record fields per OpenADR 3.1.0 specification
    properties = {
        'version': OPENADR_VERSION,
        'base_path': BASE_PATH,
        'local_url': local_url,
        'program_names': _get_program_names(),
        'requires_auth': str(requires_auth),
        'openapi_url': f'{local_url}/ui/',
    }

    _service_info = ServiceInfo(
        type_=service_type,
        name=full_name,
        port=port,
        properties=properties,
        addresses=addresses,
    )

    _zeroconf = Zeroconf()
    _zeroconf.register_service(_service_info)
    log.info(f"mdns: advertising {full_name} on port {port}")
    log.info(f"mdns: TXT records: {properties}")


def stop():
    """Unregister the mDNS service."""
    global _zeroconf, _service_info

    if _zeroconf and _service_info:
        _zeroconf.unregister_service(_service_info)
        _zeroconf.close()
        log.info("mdns: service unregistered")
        _zeroconf = None
        _service_info = None
