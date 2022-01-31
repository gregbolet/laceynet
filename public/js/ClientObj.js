/**
 * The purpose of this class is to represent the information of a client
 * */
class ClientObj {
    name;
    id;
    color;
    num;

    constructor(name, id, color, num){
      this.name = name;
      this.id = id;
      this.color = color;
      this.num = num;
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