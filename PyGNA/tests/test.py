
def run():
    try:
        import nose
    except ImportError:
        raise ImportError("The nose package is needed to run the GNA tests.")
    nose.run()

if __name__ =="__main__":
    run()