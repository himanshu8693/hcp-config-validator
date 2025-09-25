import json
import yaml
import hcl2
from pathlib import Path

def normalize_vault_hcl(parsed):
    """
    Convert HCL list-of-dicts structure to a flat dict for Vault configs.
    E.g. [ {'storage': [{'file': {}}]}, {'listener': [{'tcp': {...}}]} ]
    => { 'storage': {'type': 'file'}, 'listener': [ {'address': ..., ...} ] }
    """
    if not isinstance(parsed, list):
        return parsed
    out = {}
    for block in parsed:
        if not isinstance(block, dict):
            continue
        for k, v in block.items():
            if k == 'storage' and isinstance(v, list) and v:
                # e.g. [{'file': {}}]
                storage_type = list(v[0].keys())[0]
                out['storage'] = {'type': storage_type}
                out['storage'].update(v[0][storage_type])
            elif k == 'listener' and isinstance(v, list):
                listeners = []
                for l in v:
                    proto = list(l.keys())[0]
                    listener_conf = l[proto]
                    # Flatten: move all keys from listener_conf to top-level dict, add 'type'
                    flat_listener = dict(listener_conf)
                    flat_listener['type'] = proto
                    listeners.append(flat_listener)
                out['listener'] = listeners
            else:
                out[k] = v
    return out

def inject_vault_defaults(cfg):
    """
    Inject Vault's documented default values for missing keys.
    Only inject for keys that are not present.
    https://developer.hashicorp.com/vault/docs/configuration/reference
    """
    # Listener defaults
    if 'listener' in cfg and isinstance(cfg['listener'], list):
        for listener in cfg['listener']:
            if 'tls_disable' not in listener:
                listener['tls_disable'] = False
            if 'tls_min_version' not in listener:
                listener['tls_min_version'] = 'tls12'
            if 'tls_require_and_verify_client_cert' not in listener:
                listener['tls_require_and_verify_client_cert'] = False
            if 'address' not in listener:
                listener['address'] = '127.0.0.1:8200'
            if 'http_idle_timeout' not in listener:
                listener['http_idle_timeout'] = '5m'
            if 'http_read_timeout' not in listener:
                listener['http_read_timeout'] = '5m'
            if 'http_write_timeout' not in listener:
                listener['http_write_timeout'] = '5m'
            if 'tcp_keepalive' not in listener:
                listener['tcp_keepalive'] = '0s'
    # Top-level defaults
    if 'disable_mlock' not in cfg:
        cfg['disable_mlock'] = False
    if 'default_lease_ttl' not in cfg:
        cfg['default_lease_ttl'] = '768h'
    if 'max_lease_ttl' not in cfg:
        cfg['max_lease_ttl'] = '768h'
    if 'ui' not in cfg:
        cfg['ui'] = False
    # Add more as needed from docs
    return cfg

def inject_consul_defaults(cfg):
    """
    Inject Consul's documented default values for missing keys.
    https://developer.hashicorp.com/consul/docs/agent/config/configuration
    """
    # Example defaults (expand as needed)
    if 'datacenter' not in cfg:
        cfg['datacenter'] = 'dc1'
    if 'data_dir' not in cfg:
        cfg['data_dir'] = '/opt/consul'
    if 'log_level' not in cfg:
        cfg['log_level'] = 'INFO'
    if 'ui' not in cfg:
        cfg['ui'] = False
    if 'addresses' in cfg and isinstance(cfg['addresses'], dict):
        if 'http' not in cfg['addresses']:
            cfg['addresses']['http'] = '127.0.0.1'
    # Add more as needed
    return cfg

def inject_nomad_defaults(cfg):
    """
    Inject Nomad's documented default values for missing keys.
    https://developer.hashicorp.com/nomad/docs/configuration
    """
    if 'region' not in cfg:
        cfg['region'] = 'global'
    if 'datacenter' not in cfg:
        cfg['datacenter'] = 'dc1'
    if 'data_dir' not in cfg:
        cfg['data_dir'] = '/opt/nomad'
    if 'log_level' not in cfg:
        cfg['log_level'] = 'INFO'
    if 'enable_syslog' not in cfg:
        cfg['enable_syslog'] = False
    # Add more as needed
    return cfg

def parse_file(path: Path):
    text = path.read_text()
    # Try JSON
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try HCL2
    try:
        result = hcl2.loads(text)
        # Normalize for Vault HCL
        norm = normalize_vault_hcl(result)
        # Product detection: Vault, Consul, Nomad (simple heuristics)
        # Vault: has 'storage' and 'listener', Consul: has 'datacenter', Nomad: has 'region' or 'datacenter' and 'data_dir'
        if 'storage' in norm and 'listener' in norm:
            norm = inject_vault_defaults(norm)
        elif 'datacenter' in norm and 'data_dir' in norm and 'region' in norm:
            norm = inject_nomad_defaults(norm)
        elif 'datacenter' in norm and 'data_dir' in norm:
            norm = inject_consul_defaults(norm)
        return norm
    except Exception:
        pass
    # Try YAML
    try:
        doc = yaml.safe_load(text)
        # Product detection for YAML as well
        if isinstance(doc, dict):
            if 'storage' in doc and 'listener' in doc:
                doc = inject_vault_defaults(doc)
            elif 'datacenter' in doc and 'data_dir' in doc and 'region' in doc:
                doc = inject_nomad_defaults(doc)
            elif 'datacenter' in doc and 'data_dir' in doc:
                doc = inject_consul_defaults(doc)
        return doc
    except Exception:
        pass
    raise ValueError(f"Unsupported or malformed file: {path}")

def collect_configs(paths):
    """Given a path or list of paths, return list of (Path, parsed_dict)."""
    result = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in path.rglob('*'):
                if f.suffix.lower() in ('.hcl', '.tf', '.json', '.yaml', '.yml', '.toml'):
                    try:
                        parsed = parse_file(f)
                        result.append((f, parsed))
                    except Exception:
                        continue
        elif path.is_file():
            parsed = parse_file(path)
            result.append((path, parsed))
    return result
