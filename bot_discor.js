const { Client, GatewayIntentBits, AttachmentBuilder } = require('discord.js');
const readline = require('readline');
const fs = require('fs');
require('dotenv').config();
const token = process.env.DISCORD_TOKEN;


// Token de tu bot (obtenelo desde Discord Developer Portal)
// const token = ''; // ⚠️ REEMPLAZÁ ESTO

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ]
});

let currentChannel = null;

client.once('ready', () => {
  console.log(`✅ Bot conectado como ${client.user.tag}`);
  console.log('\n📌 Comandos disponibles:');
  console.log('-goto ID_CANAL        → Selecciona un canal');
  console.log('-name NuevoNombre     → Cambia el nombre del bot');
  console.log('-img ruta/imagen.png  → Envía una imagen al canal');
  console.log('exit                  → Cierra el bot\n');

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  rl.on('line', async (input) => {
    if (input.startsWith('-goto ')) {
      const id = input.split(' ')[1];
      const channel = client.channels.cache.get(id);
      if (channel) {
        currentChannel = channel;
        console.log(`✅ Canal seleccionado: ${channel.name}`);
      } else {
        console.log('❌ Canal no encontrado.');
      }

    } else if (input.startsWith('-name ')) {
      const newName = input.substring(6);
      try {
        await client.user.setUsername(newName);
        console.log(`✅ Nombre cambiado a: ${newName}`);
      } catch (err) {
        console.log('❌ No se pudo cambiar el nombre. (Esperá 2 horas entre cambios)');
      }

    } else if (input.startsWith('-img ')) {
      if (!currentChannel) {
        console.log('⚠️ Seleccioná un canal con -goto primero.');
        return;
      }

      const filePath = input.substring(5);
      if (!fs.existsSync(filePath)) {
        console.log('❌ Archivo no encontrado.');
        return;
      }

      const attachment = new AttachmentBuilder(filePath);
      currentChannel.send({ files: [attachment] })
        .then(() => console.log(`📤 Imagen enviada: ${filePath}`))
        .catch(err => console.error('❌ Error al enviar imagen:', err));

    } else if (input === 'exit') {
      console.log('👋 Cerrando el bot...');
      rl.close();
      client.destroy();
      process.exit();

    } else {
      if (!currentChannel) {
        console.log('⚠️ Seleccioná un canal con -goto primero.');
        return;
      }

      currentChannel.send(input)
        .then(() => console.log(`📤 Enviado: ${input}`))
        .catch(err => console.error('❌ Error al enviar mensaje:', err));
    }
  });
});

client.login(token);
