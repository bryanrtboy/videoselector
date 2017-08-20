from pssh import ParallelSSHClient, utils

output = []
hosts = ['client0', 'client1', 'client2','client3', 'client4']
client = ParallelSSHClient(hosts)

def shutdown_all():
  cmds=["shutdown now"]
  for cmd in cmds:
     output.append(client.run_command(cmd, stop_on_errors=False, sudo=True))

  for _output in output:
     client.join(_output)
     print(_output)
  print("Finished shutting down clients")

if __name__ == "__main__":
  shutdown_all()
