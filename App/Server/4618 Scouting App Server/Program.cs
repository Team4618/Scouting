using System;
using System.IO;
using System.Net.Sockets;
using System.Threading;
using InTheHand.Net.Sockets;
using Newtonsoft.Json.Linq;

namespace _4618_Scouting_App_Server
{
    class Program
    {
		static string folder = "files";
		static int port = 4618;

		static Guid uuid = new Guid("{cb3bd26c-4436-11e8-842f-0ed5f89f718b}");

		enum networkingType { hotSpot, BT, none }
		static networkingType netType = networkingType.BT;

		static string verification = "4618 SCOUTING APP";

		static void Main(string[] args)
        {
			//create directory for files if it doesn't exist
			if (!Directory.Exists(folder))
				Directory.CreateDirectory(folder);


			if (args.Length > 0)
			{
				//check for networking type
				if (args[0].ToLower() == "hotspot")
					netType = networkingType.hotSpot;
				else if (args[0].ToLower() == "bt")
					netType = networkingType.BT;
				else if (args[0].ToLower() == "none")
					netType = networkingType.none;
			}

			if (args.Length > 1) //should be location to save file
				folder = args[1].Trim();

			switch (netType) //there's gotta be a better way...
			{
				default:
					Console.WriteLine("No need for a server, just collect the JSON files from the devices at the end of the day");
					Console.WriteLine("Press any key to exit");
					Console.ReadKey();
					break;

				case networkingType.hotSpot:
					mainHotSpot();
					break;

				case networkingType.BT:
					mainBT();
					break;
			}
		}

		static void mainHotSpot()
		{
			Console.WriteLine("Creating server socket...");
			TcpListener tcpServer = new TcpListener(System.Net.IPAddress.Any, port);
			tcpServer.Start();

			while (true)
			{
				Console.WriteLine("Waiting for connection...");
				Socket socket = tcpServer.AcceptSocket();
				Console.WriteLine("Recived connection");

				new Thread(() =>
				{
					if (!handleConnection(new NetworkStream(socket)))
						socket.Close();
				}).Start();
			}
		}

		static void mainBT()
		{
			Console.WriteLine("Creating BT listener...");
			BluetoothListener btServer = new BluetoothListener(uuid);
			btServer.Start();

			while (true)
			{
				Console.WriteLine("Waiting for connection...");
				BluetoothClient client = btServer.AcceptBluetoothClient();
				new Thread(() =>
				{
					if (!handleConnection(client.GetStream()))
						client.Close();
				}).Start();
			}
		}

		static bool handleConnection(Stream s) //returns false if the connection was closed / verification unsucessful
		{
			byte[] buffer = new byte[1024];

			//first read: get verification
			//is it necessary? idk
			while (true)
			{
				if (s.CanRead)
				{
					try
					{
						//read data and see if it matches our verification
						s.Read(buffer, 0, buffer.Length);

						string msg = System.Text.Encoding.UTF8.GetString(buffer).Trim();
						msg = msg.Replace("\0", string.Empty); //remove all null chars (smh this doesn't happen in java)
						if (!msg.Equals(verification))
						{
							Console.WriteLine("Verification unsucsessful, closing");
							return false;
						}

						Console.WriteLine("Verification sucessful");
						//send verification back (probably not necessary)
						byte[] toWrite = System.Text.Encoding.UTF8.GetBytes(verification);
						s.Write(toWrite, 0, toWrite.Length);
						break;
					}
					catch (IOException ex) //connection probably closed
					{
						Console.WriteLine("Connection closed remotley");
						return false;
					}
				}
			}

			byte[] lastRead = new byte[1];
			bool lastReadEquals = false; //true if last read was equivalent to the one before it
			//second read: get the data
			while (true)
			{
				//refresh buffer
				buffer = new byte[1024];
				while (true)
				{
					if (s.CanRead)
					{
						//read the data
						s.Read(buffer, 0, buffer.Length);
	
						if (buffer.Equals(lastRead) || buffer.Equals(new byte[1024]))
						{
							if (lastReadEquals)
							{
								//its safe to assume the connection has been closed
								Console.WriteLine("Connection closed remotley");
								return false;
							}

							lastReadEquals = true;
							lastRead = buffer;
							//no need to write identical data, so start over
							continue;
						}

						lastRead = buffer;

						string msg = System.Text.Encoding.UTF8.GetString(buffer).Trim();
						msg = msg.Replace("\0", string.Empty);

						if (msg == "") //probably got sent all null bytes
							continue;

						//test to see if data is JSON formatted
						JObject msgJSON;
						try
						{
							msgJSON = JObject.Parse(msg);
						}
						catch (Newtonsoft.Json.JsonReaderException) //not JSON formatted
						{
							Console.WriteLine("Data not JSON formatted: " + msg);
							continue;
						}

						string match = msgJSON["match"].ToString().Trim();

						//check if file exists, if so append, otherwise make a new file
						JArray arr;
						if (File.Exists(folder + "/" + match + ".json"))
						{
							arr = JArray.Parse(File.ReadAllText(folder + "/" + match + ".json"));
							arr.Add(msgJSON);
						}
						else
						{
							arr = new JArray();
							arr.Add(msgJSON);
						}

						//(re) write to file
						File.WriteAllLines(folder + "/" + match + ".json", arr.ToString().Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None));
						
						Console.WriteLine("Wrote data to file " + match + ".json");
					}
				}
			}
			return true;
		}
    }
}
