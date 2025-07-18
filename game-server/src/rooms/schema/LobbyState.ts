import { ArraySchema, Schema, type } from "@colyseus/schema";
import { PlayerState } from "./PlayerState";

export class Position extends Schema {
  @type("float32") x: number = 0;
  @type("float32") z: number = 0;

  constructor(x: number = 0, z: number = 0) {
    super();
    this.x = x;
    this.z = z;
  }
}

export class Name extends Schema {
  @type("string") name: string = "";

  constructor(name: string = "") {
    super();
    this.name = name;
  }
}

export class LobbyState extends Schema {
  @type({ map: PlayerState }) players = new Map<string, PlayerState>();
  @type("int32") onLevel = 2;
  @type([Name]) killedEntities = new Array();
  @type([Position]) markerPosition = new Array();
}