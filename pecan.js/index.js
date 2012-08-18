module.exports = Site

var $ = require('br-jquery')
  , plate = require('plate')
  , route = require('./routes')
  , request = require('./request')

function Site() {
  this.root = null
  this._tplCache = {}
}

var cons = Site
  , proto = cons.prototype

proto.init = function(body, templates) {
  var fn = route(window.location.pathname)
    , self = this

  self.root = $(body)

  $('body').on('click', function(ev) {
    if(ev.target.host !== window.location.host)
      return

    ev.preventDefault()

    fn(self)
  })

  fn(self) 
}

proto.render = function(name, context, ready) {
  var self = this

  self.cachedTemplate(name).render(context, function(err, data) {
    self.root.html(data)
    self.root.removeClass('loading')

    ready(null, self.root)  
  })  
}

proto.cachedTemplate = function(name) {
  var tpl = this._tplCache[name]
  if(!tpl) {
    tpl = new plate.Template(templates[name] || '')
  }
  this._tplCache[name] = tpl
  return tpl
}

proto.schema = function(name, ready) {
  var self = this
    , key = 'schema:'+name
    , schema = self.storage.get(key)
  
  if(schema) {
    return ready(null, schema)
  }

  self.schemaAll(gotSchema)

  function gotSchema(err, data) {
    if(err) return ready(err)

    if(!data[name] || !data[name].schema) {
      return ready(new Error('schema was borked'))
    }

    request.get(data[name].schema, {}, {}, function(err, data) {
      if(err) {
        return ready(err)
      }
      self.storage.set(key, data)
      return ready(null, data)
    })
  }
}

proto.schemaAll = function(ready) {
  var self = this
    , schema = self.storage.get('schema')

  if(schema)
    return ready(null, schema)

  request.get(self.apiURL(), function(err, data) {
    if(err) return ready(err)

    self.storage.set('schema', data)
    return ready(null, data)
  })
}

proto.storage = {
  get: getStorage
, set: setStorage
}

function getStorage(key) {
  localStorage.get(key)
}

function setStorage(key, value) {
  localStorage.set(key, value)
}
