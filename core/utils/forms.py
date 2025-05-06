def limpiar_campos_en_recarga(*campos):
    def decorador(form_class):
        original_init = form_class.__init__

        def nuevo_init(self, *args, **kwargs):
            data = kwargs.get('data')
            if data and data.get('_recarga_por_seccion') == '1':
                data = data.copy()
                for campo in campos:
                    data[campo] = ''
                kwargs['data'] = data
                self._recarga_por_seccion = True
            else:
                self._recarga_por_seccion = False

            original_init(self, *args, **kwargs)

        form_class.__init__ = nuevo_init
        return form_class
    return decorador
