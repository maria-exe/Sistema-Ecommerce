clientes_sse = {}   
historico = {}     
loop = None       

def notificar(id_pedido, msg):
    historico.setdefault(id_pedido, []).append(msg)
    if loop is None:
        return
    for fila in list(clientes_sse.get(id_pedido, [])):
        loop.call_soon_threadsafe(fila.put_nowait, msg)