def main():
    import sftdyn.args as args
    import sftdyn.server

    vars(args).update(args.parse())
    try:
        sftdyn.server.serve()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
