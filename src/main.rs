use std::path::PathBuf;

use structopt::StructOpt;

mod converter;

#[derive(Debug, StructOpt)]
#[structopt(name = "linear-tools")]
struct Cli {
    #[structopt(
        short,
        long,
        help = "Converts regions to the Anvil (MCA) format",
        hide_default_value = true
    )]
    mca: bool,

    #[structopt(
        short,
        long,
        help = "Converts regions to the Linear format",
        hide_default_value = true
    )]
    linear: bool,

    #[structopt(
        short,
        long,
        default_value = "0",
        help = "Sets the verbosity level of the output",
        hide_default_value = true
    )]
    verbose: u16,

    #[structopt(
        short,
        long,
        default_value = "1",
        help = "Sets the number of threads to use for conversion",
        hide_default_value = true
    )]
    threads: u16,

    #[structopt(
        short,
        long,
        default_value = "6",
        help = "Sets compression level for linear conversion (1-22)",
        hide_default_value = true
    )]
    compression: u8,

    #[structopt(parse(from_os_str))]
    input: PathBuf,

    #[structopt(short = "i", long = "input", help = "")]
    output: Option<PathBuf>,
}

fn validate_args(args: &mut Cli) {
    // Validate conversion method
    if args.linear && args.mca {
        eprintln!("Error: --mca and --linear cannot both be enabled",);
        std::process::exit(1);
    }

    // Set default thread count to the number of cpus
    if args.threads == 0 {
        args.threads = num_cpus::get() as u16;
    }
}

fn main() {
    let mut cli = Cli::from_args();
    validate_args(&mut cli);

    print!("{:?}", cli)
}
