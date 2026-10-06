# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response


class GameStoreApiController(http.Controller):
    """API REST JSON para GameStore Manager.
    
    Permite consultar catálogo, stock y crear pedidos desde aplicaciones externas
    (móviles, e-commerce, terminal de punto de venta independiente).
    """

    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data, default=str),
            status=status,
            content_type='application/json; charset=utf-8'
        )

    # Catálogo y Videojuegos
    @http.route('/api/gamestore/games', type='http', auth='public', methods=['GET'], csrf=False)
    def get_games(self, **kwargs):
        """Lista el catálogo de videojuegos con filtros opcionales.
        
        Parámetros query soportados:
          - plataforma: nombre de la plataforma (ej. ?plataforma=Nintendo Switch)
          - estado_stock: disponible | bajo | agotado
          - search: búsqueda por nombre
        """
        domain = [('active', '=', True)]
        if kwargs.get('plataforma'):
            domain.append(('plataforma_id.name', 'ilike', kwargs['plataforma']))
        if kwargs.get('estado_stock'):
            domain.append(('estado_stock', '=', kwargs['estado_stock']))
        if kwargs.get('search'):
            domain.append(('name', 'ilike', kwargs['search']))

        games = request.env['gamestore.videojuego'].sudo().search(domain)
        result = []
        for g in games:
            result.append({
                'id': g.id,
                'name': g.name,
                'plataforma': g.plataforma_id.name,
                'plataforma_id': g.plataforma_id.id,
                'generos': [gen.name for gen in g.genero_ids],
                'desarrolladora': g.desarrolladora_id.name if g.desarrolladora_id else None,
                'precio': g.precio,
                'moneda': g.currency_id.name,
                'stock': g.stock,
                'estado_stock': g.estado_stock,
                'pegi': g.pegi,
                'unidades_vendidas': g.unidades_vendidas,
            })

        return self._json_response({'status': 'success', 'count': len(result), 'data': result})

    @http.route('/api/gamestore/games/<int:game_id>', type='http', auth='public', methods=['GET'], csrf=False)
    def get_game_detail(self, game_id, **kwargs):
        """Detalle completo de un videojuego por ID."""
        game = request.env['gamestore.videojuego'].sudo().browse(game_id)
        if not game.exists():
            return self._json_response({'status': 'error', 'message': 'Videojuego no encontrado'}, status=404)

        data = {
            'id': game.id,
            'name': game.name,
            'plataforma': game.plataforma_id.name,
            'generos': [gen.name for gen in game.genero_ids],
            'desarrolladora': game.desarrolladora_id.name if game.desarrolladora_id else None,
            'fecha_lanzamiento': game.fecha_lanzamiento,
            'pegi': game.pegi,
            'precio': game.precio,
            'moneda': game.currency_id.name,
            'stock': game.stock,
            'stock_minimo': game.stock_minimo,
            'estado_stock': game.estado_stock,
            'unidades_vendidas': game.unidades_vendidas,
            'descripcion': game.descripcion or '',
        }
        return self._json_response({'status': 'success', 'data': data})

    @http.route('/api/gamestore/platforms', type='http', auth='public', methods=['GET'], csrf=False)
    def get_platforms(self, **kwargs):
        """Lista de plataformas disponibles con conteo de videojuegos."""
        platforms = request.env['gamestore.plataforma'].sudo().search([])
        data = [{
            'id': p.id,
            'name': p.name,
            'fabricante': p.fabricante,
            'videojuego_count': p.videojuego_count,
        } for p in platforms]
        return self._json_response({'status': 'success', 'data': data})

    # Creación de Pedidos
    @http.route('/api/gamestore/orders', type='http', auth='public', methods=['POST'], csrf=False)
    def create_order(self, **kwargs):
        """Crea un pedido en estado Borrador o Confirmado.
        
        Body JSON esperado:
        {
            "cliente_id": 1,
            "confirmar": true,   // opcional: valida y descuenta stock inmediatamente
            "lineas": [
                {"videojuego_id": 1, "cantidad": 2},
                {"videojuego_id": 3, "cantidad": 1}
            ],
            "notas": "Pedido desde API e-commerce"
        }
        """
        try:
            body = json.loads(request.httprequest.data.decode('utf-8'))
        except Exception:
            return self._json_response({'status': 'error', 'message': 'JSON inválido en el cuerpo de la petición'}, status=400)

        cliente_id = body.get('cliente_id')
        lineas_data = body.get('lineas', [])
        confirmar = body.get('confirmar', False)
        notas = body.get('notas', '')

        if not cliente_id:
            return self._json_response({'status': 'error', 'message': 'El campo cliente_id es obligatorio'}, status=400)
        
        partner = request.env['res.partner'].sudo().browse(cliente_id)
        if not partner.exists():
            return self._json_response({'status': 'error', 'message': f'Cliente ID {cliente_id} no existe'}, status=404)

        if not lineas_data:
            return self._json_response({'status': 'error', 'message': 'Debe incluir al menos una línea con videojuego_id y cantidad'}, status=400)

        # Construir comandos de Odoo para One2many: (0, 0, valores)
        lineas_vals = []
        for l in lineas_data:
            vid = l.get('videojuego_id')
            cant = l.get('cantidad', 1)
            juego = request.env['gamestore.videojuego'].sudo().browse(vid)
            if not juego.exists():
                return self._json_response({'status': 'error', 'message': f'Videojuego {vid} no existe'}, status=404)
            lineas_vals.append((0, 0, {
                'videojuego_id': vid,
                'cantidad': cant,
            }))

        try:
            pedido = request.env['gamestore.pedido'].sudo().create({
                'cliente_id': cliente_id,
                'linea_ids': lineas_vals,
                'notas': f'<p>{notas}</p>' if notas else False,
            })

            if confirmar:
                pedido.action_confirmar()

            return self._json_response({
                'status': 'success',
                'message': 'Pedido creado exitosamente',
                'data': {
                    'id': pedido.id,
                    'reference': pedido.name,
                    'estado': pedido.estado,
                    'total': pedido.total,
                    'moneda': pedido.currency_id.name,
                    'cantidad_total': pedido.cantidad_total,
                }
            }, status=201)

        except Exception as e:
            return self._json_response({'status': 'error', 'message': str(e)}, status=400)
