// Examples
var Person = Class.create();
Person.prototype = {
  initialize: function(name) {
    this.name = name;
  },
  say: function(message) {
    return this.name + ': ' + message;
  }
};
    
var guy = new Person('Miro');
guy.say('hi');
    
var Pirate = Class.create();
// inherit from Person class:
Pirate.prototype = Object.extend(new Person(), {
  // redefine the speak method
  say: function(message) {
    return this.name + ': ' + message + ', yarr!';
  }
});
    
var john = new Pirate('Long John');
console.log(john.say('ahoy matey'))



var Camera = Class.create();
Camera.prototype = {
  initialize: function(name) {
    this.name = name;
  },
//   say: function(message) {
//     return this.name + ': ' + message;
//   }
};