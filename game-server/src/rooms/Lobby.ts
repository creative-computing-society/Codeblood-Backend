import { Room, Client } from "@colyseus/core";
import { PlayerState, JoinOptions } from "./schema/PlayerState";
import { LobbyState, Name, Position } from "./schema/LobbyState";
import { JoinCode } from "../joinCode";
import fs from "fs";
import path from "path";

type CreateOptions = {
  joinCode: string;
}
type GameOptions = {
  level: number;
}

const SAVE_DIR = "./saves";

function saveStateToDisk(roomId: string, state: any) {
  const filePath = path.join(SAVE_DIR, `${roomId}.json`);
  fs.mkdirSync(SAVE_DIR, { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(state));
}

function loadStateFromDisk(roomId: string): any | null {
  const filePath = path.join(SAVE_DIR, `${roomId}.json`);
  if (!fs.existsSync(filePath)) return null;
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}


export class Lobby extends Room<LobbyState> {
  maxClients = 4;
  state = new LobbyState();
  joinCode: string | null = null;

  onCreate (options: CreateOptions) {
    this.joinCode = options.joinCode;
    const savedState = loadStateFromDisk(options.joinCode);
    if (savedState != null) {
      this.state = savedState;
    }
    this.autoDispose = false; // if all players leave, the room will not be disposed automatically
    if (!options.joinCode) {
      return;
    }
    this.state.onLevel = 2;
    JoinCode.getInstance().addCode(options.joinCode, this.roomId);
    this.onMessage("update", (client, message) => {
      const player = this.state.players.get(client.sessionId);
      if (!player) {
        return;
      }
      player.x = message.x || player.x;
      player.y = message.y || player.y;
      player.z = message.z || player.z;
      player.a = message.a || player.a;
      player.b = message.b || player.b;
      player.c = message.c || player.c;
      player.d = message.d || player.d;
    });
    this.onMessage("game", (client, message: GameOptions) => {
      const player = this.state.players.get(client.sessionId);
      if (!player) {
        return;
      }
      console.log("Going to level: ", message.level, "in room", this.roomId);
      this.state.onLevel = message.level;
      this.broadcast("game", message);
    });
    // this.onMessage("respawn", (client, message) => {
    //   const player = this.state.players.get(client.sessionId);
    //   if (!player) {
    //     return;
    //   }
    //   console.log("Respawning player", client.sessionId, "in room", this.roomId);
    //   this.broadcast("respawn");
    // });
    this.onMessage("entityDeath", (client, message) => {
      const player = this.state.players.get(client.sessionId);
      if (!player) {
        return;
      }
      console.log("Entity death reported by", client.sessionId, "in room", this.roomId, "for entity:", message.name);
      this.state.killedEntities.push(new Name(message.name));
      this.broadcast("entityDeath", message);
      saveStateToDisk(options.joinCode, this.state);
    });
    this.onMessage("spawnMarker", (client, message) => {
      const player = this.state.players.get(client.sessionId);
      if (!player) {
        return;
      }
      console.log("Spawn marker reported by", client.sessionId, "in room", this.roomId, "at position:: x: ", message.x, ", z: ", message.z);
      this.state.markerPosition.push(new Position(message.x, message.z));
      this.broadcast("spawnMarker", message);
      saveStateToDisk(options.joinCode, this.state);
    });
    this.onMessage("enemyUpdate", (client, message) => {
      const player = this.state.players.get(client.sessionId);
      if (!player) {
        return;
      }
      this.broadcast("enemyUpdate", message);
    })
  }

  onJoin (client: Client, options: JoinOptions) {
    console.log(client.sessionId, "joined! ", JSON.stringify(options));
    this.state.players.set(client.sessionId, new PlayerState(options));
  }

  onLeave (client: Client, consented: boolean) {
    this.state.players.delete(client.sessionId);
    this.broadcast("playerLeave", client.sessionId);
    saveStateToDisk(this.joinCode, this.state);
  }

  onDispose() {
    JoinCode.getInstance().removeLobbyId(this.roomId);
    console.log("room", this.roomId, "disposing...");
    this.state.players.clear();
    saveStateToDisk(this.joinCode, this.state);
  }

}
