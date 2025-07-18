export class JoinCode {
    private data: Map<string, string>;

    private static instance: JoinCode;

    private constructor() {
        this.data = new Map<string, string>();
    }
    static getInstance(): JoinCode {
        if (!JoinCode.instance) {
            JoinCode.instance = new JoinCode();
        }
        return JoinCode.instance;
    }

    addCode(code: string, lobbyId: string): void {
        this.data.set(code.slice(0, 8), lobbyId);
        console.log("Data now: ", this.data)
    }

    getLobbyId(code: string): string | undefined {
        code = code.slice(0, 8);
        const output = this.data.get(code);
        console.log(`Query: ${code}, Result: ${output} `)
        return output;
    }

    removeLobbyId(lobbyId: string): void {
        for (const [code, id] of this.data.entries()) {
            if (id === lobbyId) {
                this.data.delete(code);
                console.log(`Removed code: ${code} for lobbyId: ${lobbyId}`);
                break;
            }
        }
    }
}