import { Schema, type } from "@colyseus/schema";

export class PlayerState extends Schema {
  // Position
  @type("number") x: number = 0;
  @type("number") y: number = 0;
  @type("number") z: number = 0;

  // Rotation
  @type("number") a: number = 0;
  @type("number") b: number = 0;
  @type("number") c: number = 0;
  @type("number") d: number = 0;

  // Player type
  @type("int32") type: number = 0;

  // Player name
  @type("string") name: string = "";

  constructor(options: JoinOptions) {
    super();
    this.type = options.type || 0;
    this.name = options.name || "Unknown";
  }
}

export type JoinOptions = {
  joinCode: string;
  type: number;
  name: string;
}