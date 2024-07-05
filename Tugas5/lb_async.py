import asyncio
import socket
import logging

class BackendList:
    def __init__(self):
        self.servers = []
        self.servers.append(('127.0.0.1', 8000))
        self.servers.append(('127.0.0.1', 8001))
        self.servers.append(('127.0.0.1', 8002))
        # self.servers.append(('127.0.0.1',9005))
        self.current = 0

    def getserver(self):
        s = self.servers[self.current]
        self.current = self.current + 1
        if self.current >= len(self.servers):
            self.current = 0
        return s

class Backend(asyncio.Protocol):
    def __init__(self, client_transport, target_address):
        self.client_transport = client_transport
        self.target_address = target_address
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        try:
            self.transport.write(data)
        except:
            pass

    def connection_lost(self, exc):
        if self.transport:
            self.transport.close()
        if self.client_transport:
            self.client_transport.close()

class ProcessTheClient(asyncio.Protocol):
    def __init__(self, server):
        self.server = server
        self.backend_transport = None

    def connection_made(self, transport):
        self.client_transport = transport
        server_address = self.server.getserver()
        asyncio.ensure_future(self.connect_to_backend(server_address))

    async def connect_to_backend(self, server_address):
        loop = asyncio.get_event_loop()
        transport, protocol = await loop.create_connection(lambda: Backend(self.client_transport, server_address), server_address[0], server_address[1])
        self.backend_transport = transport

    def data_received(self, data):
        if self.backend_transport:
            self.backend_transport.write(data)

    def connection_lost(self, exc):
        if self.backend_transport:
            self.backend_transport.close()
        if self.client_transport:
            self.client_transport.close()

async def main(port):
    server = BackendList()
    loop = asyncio.get_running_loop()
    server_coro = await loop.create_server(lambda: ProcessTheClient(server), '0.0.0.0', port)
    logging.warning(f"Server running on port {port}")
    async with server_coro:
        await server_coro.serve_forever()

if __name__ == "__main__":
    portnumber = 55555
    asyncio.run(main(portnumber))
