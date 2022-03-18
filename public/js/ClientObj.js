/**
 * The purpose of this class is to represent the information of a client
 * */
class ClientObj {
    name;
    id;
    color;
    num;
    img;

    constructor(name, id, color, num, img){
      this.name = name; // char name
      this.id = id; // socket id
      this.color = color; // stay the same within a single game
      this.num = num;
      this.img = img;
    }

    // getName() {
    //   return this.#name;
    // }

    // getId() {
    //   return this.#id;
    // }

    // getColor() {
    //   return this.#color;
    // }

    // getNum() {
    //   return this.#num;
    // }

    // setName(newName){
    //     this.#name = newName;
    // }

    // setID(newID){
    //     this.#id = newID;
    // }

    // setColor(newCol){
    //     this.#id = newCol;
    // }

    // setNum(newNum) {
    //     this.#num = newNum;
    // }
  }

  if (typeof module === 'object') module.exports = ClientObj;