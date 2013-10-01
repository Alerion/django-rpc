
var djangoRPC = {};

djangoRPC.utils = (function(){

    var utils = {};

    utils.noop = function(){};

    utils.isObject = function(v){
        return !!v && Object.prototype.toString.call(v) === '[object Object]';
    }

    utils.namespace = function(){
        for (var argIndex = 0, argsLength = arguments.length; argIndex < argsLength; argIndex += 1)
        {
            var scope = window;
            var path = arguments[argIndex].split('.');
            for (var pathIndex = 0, pathLength = path.length; pathIndex < pathLength; pathIndex += 1)
            {
                scope = scope[path[pathIndex]] = scope[path[pathIndex]] || {};
            }
        }

        return scope;
    }


    utils.merge = function(target, source)
    {
        for (var key in source)
        {
            if (!source.hasOwnProperty(key))
            {
                continue;
            }

            target[key] = source[key];
        }

        return target;
    }


    utils.define = (function(){
        var prototype = function(){};
        return function(properties){

            // Super constructor passed
            if (properties.hasOwnProperty('__super__'))
            {
                var __super__ = properties.__super__;
                if (typeof(__super__) === 'function')
                {
                    var __init__ = properties.hasOwnProperty('__init__')
                    ? properties.__init__
                    : function(){__super__.apply(this, arguments)};

                    prototype.prototype = properties.__super__.prototype;
                    __init__.prototype = new prototype();
                    __init__.__super__ = __super__;
                }
                else
                {
                    var __init__ = properties.hasOwnProperty('__init__')
                    ? properties.__init__
                    : function(){__super__.apply(this, arguments)};

                    prototype.prototype = __super__;
                    __init__.prototype = new prototype();
                    __init__.__super__ = __super__.constructor;
                }
            }
            else
            {
                var __init__ = properties.hasOwnProperty('__init__')
                ? properties.__init__
                : function(){};

                __init__.prototype = {};
            }

            utils.merge(__init__.prototype, properties);
            __init__.prototype.constructor = __init__;

            return __init__;
        }
    })();


    utils.JSON = {
        useHasOwn: ({}.hasOwnProperty ? true : false),
        pad: function(n){
            return n < 10 ? "0" + n : n;
        },
        m: {
            "\b": '\\b',
            "\t": '\\t',
            "\n": '\\n',
            "\f": '\\f',
            "\r": '\\r',
            '"': '\\"',
            "\\": '\\\\'
        },
        encodeString: function(s){
            if (/["\\\x00-\x1f]/.test(s)) {
                return '"' +
                s.replace(/([\x00-\x1f\\"])/g, function(a, b){
                    var c = utils.JSON.m[b];
                    if (c) {
                        return c;
                    }
                    c = b.charCodeAt();
                    return "\\u00" +
                    Math.floor(c / 16).toString(16) +
                    (c % 16).toString(16);
                }) +
                '"';
            }
            return '"' + s + '"';
        },
        encodeArray: function(o){
            var a = ["["], b, i, l = o.length, v;
            for (i = 0; i < l; i += 1) {
                v = o[i];
                switch (typeof v) {
                    case "undefined":
                    case "function":
                    case "unknown":
                        break;
                    default:
                        if (b) {
                            a.push(',');
                        }
                        a.push(v === null ? "null" : this.encode(v));
                        b = true;
                }
            }
            a.push("]");
            return a.join("");
        },
        encodeDate: function(o){
            return '"' + o.getFullYear() + "-" +
            this.pad(o.getMonth() + 1) +
            "-" +
            this.pad(o.getDate()) +
            "T" +
            this.pad(o.getHours()) +
            ":" +
            this.pad(o.getMinutes()) +
            ":" +
            this.pad(o.getSeconds()) +
            '"';
        },
        encode: function(o){
            if (typeof o == "undefined" || o === null) {
                return "null";
            }
            else
                if (o instanceof Array) {
                    return this.encodeArray(o);
                }
                else
                    if (o instanceof Date) {
                        return this.encodeDate(o);
                    }
                    else
                        if (typeof o == "string") {
                            return this.encodeString(o);
                        }
                        else
                            if (typeof o == "number") {
                                return isFinite(o) ? String(o) : "null";
                            }
                            else
                                if (typeof o == "boolean") {
                                    return String(o);
                                }
                                else {
                                    var self = this;
                                    var a = ["{"], b, i, v;
                                    for (i in o) {
                                        if (!this.useHasOwn || o.hasOwnProperty(i)) {
                                            v = o[i];
                                            switch (typeof v) {
                                                case "undefined":
                                                case "function":
                                                case "unknown":
                                                    break;
                                                default:
                                                    if (b) {
                                                        a.push(',');
                                                    }
                                                    a.push(self.encode(i), ":", v === null ? "null" : self.encode(v));
                                                    b = true;
                                            }
                                        }
                                    }
                                    a.push("}");
                                    return a.join("");
                                }
        },
        decode: function(json){
            return eval("(" + json + ')');
        }
    };


    utils.Event = utils.define({
        __init__: function(obj, name){
            this.name = name;
            this.obj = obj;
            this.listeners = [];
        },

        addListener: function(fn, scope, options){
            var me = this, l;
            scope = scope || me.obj;
            if (!me.isListening(fn, scope)) {
                l = me.createListener(fn, scope, options);
                if (me.firing) { // if we are currently firing this event, don't disturb the listener loop
                    me.listeners = me.listeners.slice(0);
                }
                me.listeners.push(l);
            }
        },

        createListener: function(fn, scope, o){
            o = o || {}, scope = scope || this.obj;
            var l = {
                fn: fn,
                scope: scope,
                options: o
            }, h = fn;
            l.fireFn = h;
            return l;
        },

        isListening: function(fn, scope){
            return this.findListener(fn, scope) != -1;
        },

        findListener: function(fn, scope){
            var list = this.listeners, i = list.length, l;

            scope = scope || this.obj;
            while (i--) {
                l = list[i];
                if (l) {
                    if (l.fn == fn && l.scope == scope) {
                        return i;
                    }
                }
            }
            return -1;
        },

        removeListener: function(fn, scope){
            var index, l, k, me = this, ret = false;
            if ((index = me.findListener(fn, scope)) != -1) {
                if (me.firing) {
                    me.listeners = me.listeners.slice(0);
                }
                l = me.listeners[index];
                if (l.task) {
                    l.task.cancel();
                    delete l.task;
                }
                k = l.tasks && l.tasks.length;
                if (k) {
                    while (k--) {
                        l.tasks[k].cancel();
                    }
                    delete l.tasks;
                }
                me.listeners.splice(index, 1);
                ret = true;
            }
            return ret;
        },

        // Iterate to stop any buffered/delayed events
        clearListeners: function(){
            var me = this, l = me.listeners, i = l.length;
            while (i--) {
                me.removeListener(l[i].fn, l[i].scope);
            }
        },

        fire: function(){
            var me = this, args = Array.prototype.slice.call(arguments, 0), listeners = me.listeners, len = listeners.length, i = 0, l;

            if (len > 0) {
                me.firing = true;
                for (; i < len; i++) {
                    l = listeners[i];
                    if (l && l.fireFn.apply(l.scope || me.obj || window, args) === false) {
                        return (me.firing = false);
                    }
                }
            }
            me.firing = false;
            return true;
        }
    });


    utils.Observer = utils.define({
        __init__: function(){

            var me = this, e = me.events;
            if (me.listeners) {
                me.addListener(me.listeners);
                delete me.listeners;
            }
            me.events = e || {};
        },

        // private
        filterOptRe: /^(?:scope|delay|buffer|single)$/,

        fireEvent: function(){
            var a = Array.prototype.slice.call(arguments, 0), ename = a[0].toLowerCase(), me = this, ret = true, ce = me.events[ename], q, c;
            if (me.eventsSuspended === true) {
                if (q = me.eventQueue) {
                    q.push(a);
                }
            }
            else
                if (utils.isObject(ce) && ce.bubble) {
                    if (ce.fire.apply(ce, a.slice(1)) === false) {
                        return false;
                    }
                    c = me.getBubbleTarget && me.getBubbleTarget();
                    if (c && c.enableBubble) {
                        if (!c.events[ename] || !utils.isObject(c.events[ename]) || !c.events[ename].bubble) {
                            c.enableBubble(ename);
                        }
                        return c.fireEvent.apply(c, a);
                    }
                }
                else {
                    if (utils.isObject(ce)) {
                        a.shift();
                        ret = ce.fire.apply(ce, a);
                    }
                }
            return ret;
        },

        addListener: function(eventName, fn, scope, o){
            var me = this, e, oe, isF, ce;
            if (utils.isObject(eventName)) {
                o = eventName;
                for (e in o) {
                    oe = o[e];
                    if (!me.filterOptRe.test(e)) {
                        me.addListener(e, oe.fn || oe, oe.scope || o.scope, oe.fn ? oe : o);
                    }
                }
            }
            else {
                eventName = eventName.toLowerCase();
                ce = me.events[eventName] || true;
                if (typeof ce === 'boolean') {
                    me.events[eventName] = ce = new utils.Event(me, eventName);
                }
                ce.addListener(fn, scope, utils.isObject(o) ? o : {});
            }
        },

        removeListener: function(eventName, fn, scope){
            var ce = this.events[eventName.toLowerCase()];
            if (utils.isObject(ce)) {
                ce.removeListener(fn, scope);
            }
        },

        purgeListeners: function(){
            var events = this.events, evt, key;
            for (key in events) {
                evt = events[key];
                if (utils.isObject(evt)) {
                    evt.clearListeners();
                }
            }
        },

        addEvents: function(o){
            var me = this;
            me.events = me.events || {};
            if (typeof o === 'string') {
                var a = arguments, i = a.length;
                while (i--) {
                    me.events[a[i]] = me.events[a[i]] || true;
                }
            }
            else {
                Ext.applyIf(me.events, o);
            }
        },

        hasListener: function(eventName){
            var e = this.events[eventName.toLowerCase()];
            return utils.isObject(e) && e.listeners.length > 0;
        }
    });

    utils.DelayedTask = function(fn, scope, args){
        var me = this,
            id,
            call = function(){
                clearInterval(id);
                id = null;
                fn.apply(scope, args || []);
            };

        me.delay = function(delay, newFn, newScope, newArgs){
            me.cancel();
            fn = newFn || fn;
            scope = newScope || scope;
            args = newArgs || args;
            id = setInterval(call, delay);
        };

        me.cancel = function(){
            if(id){
                clearInterval(id);
                id = null;
            }
        };
    };

    return utils;

})();