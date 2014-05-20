import sftdyn.args
import sftdyn.server


def main():
    sftdyn.args.__dict__.update(sftdyn.args.parse().__dict__)
    try:
        sftdyn.server.serve()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
