class DaisysMcpError(Exception):
    pass


def throw_mcp_error(message: str):
    raise DaisysMcpError(message)
