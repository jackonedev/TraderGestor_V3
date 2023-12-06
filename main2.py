#  DEASARROLLO DE LA SECCION DE COLOCAR ORDENES



################################################################################################
################################################################################################
################################################################################################
#########################              PROGRAMA PRINCIPAL              #########################
################################################################################################
################################################################################################
################################################################################################


if __name__ == '__main__':
    from tools.api_bingx import get_price
    from tools.api_bingx_v2 import switch_leverage, post_order
    from tools.app_modules import ultimas_ordenes, seleccionar_orden, buscar_orden, leer_orden
    from tools.ingresar_datos import ingreso_bool

    print ('''
    ============================================================
            BIENVENIDO A LA MEJOR CALCULADORA DE RIESGO
    ============================================================
TradeGestorDEMO v2
Exchange: BingX
Cuenta: Future Perpetual
COLOCACION DE ORDENES

    ''')

    # INGRESAR ARCHIVO DE ORDENES

    posible_files = ultimas_ordenes()
    num_orden = seleccionar_orden(posible_files)
    file = buscar_orden(num_orden, posible_files)


    # LEER INFORMACION DE LAS ORDENES

    direccion_trade, contrato, target_entradas, apalancamiento, monto_entrada = leer_orden(file)

    # EMPAQUETAR ORDENES
    spread = 0.0005  #0.05%
    symbol = contrato['symbol']
    positionSide = direccion_trade

    if positionSide == 'LONG':
        entrada_side = 'BUY'
        sl_side = 'SELL'
    elif positionSide == 'SHORT':
        entrada_side = 'SELL'
        sl_side = 'BUY'

    ordenes = []
    for i in range(len(target_entradas)):
        entrada = {}
        sl = {}

        type_entrada = target_entradas[i][1]
        type_sl = 'TRIGGER_MARKET'#STOP_MARKET: promedia los stoploss

        if type_entrada=='TRIGGER_MARKET':
            benchmark = get_price(symbol)
            if positionSide == 'LONG':
                stopPrice = benchmark * (1 - spread)
            elif positionSide == 'SHORT':
                stopPrice = benchmark * (1 + spread)

        quantity = monto_entrada[i]
        
        orden = {
            "symbol": symbol,
            "positionSide": positionSide,
            'quantity': quantity
        }

        entrada.update(orden)
        entrada.update({'side': entrada_side,'type': type_entrada})
        sl.update(orden)
        sl.update({'side': sl_side,'type': type_sl, 'stopPrice': target_entradas[i][-1]})

        if type_entrada.find('LIMIT') != -1:
            entrada.update({'price': target_entradas[i][0]})
        elif type_entrada.find('TRIGGER') != -1:
            entrada.update({'stopPrice':stopPrice})

        ordenes.append((entrada, sl))

    # MOSTRAR ORDENES

    print('''
    ============================================================
    ORDENES A COLOCAR
    ============================================================
    ''')

    for i in range(len(target_entradas)):
        print(f'''
        ORDEN DE ENTRADA {i}
        ''')
        print(ordenes[i][0])
        print(f'''
        ORDEN DE STOP LOSS {i}
        ''')
        print(ordenes[i][1])

    
    
    # CAMBIAR EL APALANCAMIENTO DEL PAR
    try:
        response = switch_leverage(symbol, direccion_trade, apalancamiento)
        #TODO: si existe una orden abierta saltear este paso
        pass
    except:
        pass

    if response['code'] == 0:
        print ('Actualización de apalancamiento OK: {}'.format(response['data']))
    else:
        print ('Error al actualizar el apalancamiento: {}'.format(response['msg']))
        exit()

    continuar = ingreso_bool('\nContinuar?')
    if not continuar:
        print ('operacion abortada')
        exit()
    # COLOCACION DE LAS ORDENES
    responses = []
    for i in range(len(target_entradas)):

        response_entrada = post_order(**ordenes[i][0])

        if response_entrada['code'] == 0:
            print ('Orden de entrada OK: {}'.format(response['data']))
        else:
            print ('Error al colocar la orden de entrada: {}'.format(response['msg']))
            exit()

        response_sl = post_order(**ordenes[i][1])

        if response['code'] == 0:
            print ('Orden de stop loss OK: {}'.format(response['data']))
        else:
            print ('Error al colocar la orden de stop loss: {}'.format(response['msg']))
            exit()

        responses.append((response_entrada, response_sl))
    # EXPORTAR DATOS DEL TRADE
