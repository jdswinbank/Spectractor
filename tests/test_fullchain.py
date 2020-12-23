from numpy.testing import run_module_suite
from scipy.interpolate import interp1d

from spectractor import parameters
from spectractor.extractor.images import Image
from spectractor.extractor.spectrum import Spectrum
from spectractor.extractor.extractor import Spectractor
from spectractor.logbook import LogBook
from spectractor.config import load_config
from spectractor.simulation.image_simulation import ImageSim
from spectractor.tools import plot_spectrum_simple
from spectractor.fit.fit_spectrum import SpectrumFitWorkspace, run_spectrum_minimisation
from spectractor.fit.fit_spectrogram import SpectrogramFitWorkspace, run_spectrogram_minimisation
import os
import numpy as np
import matplotlib.pyplot as plt

PSF_POLY_ORDER = 2
PSF_POLY_PARAMS_TRUTH = [1, 0, 0,
                         0, 0, 0,
                         3, 2, 0,
                         2, 0, 0,
                         500]
A1_T = 1
A2_T = 1


def plot_residuals(spectrum, lambdas_truth, amplitude_truth):
    """

    Parameters
    ----------
    spectrum
    lambdas_truth
    amplitude_truth

    Examples
    --------

    >>> from spectractor.extractor.spectrum import Spectrum
    >>> image = Image("./tests/data/sim_20170530_134.fits")
    >>> spectrum = Spectrum("./tests/data/sim_20170530_134_spectrum.fits")
    >>> lambdas_truth = np.fromstring(image.header['LBDAS_T'][1:-1], sep=' ')
    >>> amplitude_truth = np.fromstring(image.header['AMPLIS_T'][1:-1], sep=' ', dtype=float)[:lambdas_truth.size]
    >>> plot_residuals(spectrum, lambdas_truth, amplitude_truth)
    """
    fig, ax = plt.subplots(2, 1, figsize=(8, 6), sharex="all", gridspec_kw={'height_ratios': [3, 1]})
    plot_spectrum_simple(ax[0], spectrum.lambdas, spectrum.data, data_err=spectrum.err, label="Fit",
                         units=spectrum.units)
    # spectrum.lines.plot_atomic_lines(ax[0], fontsize=12, force=True)
    ax[0].plot(lambdas_truth, amplitude_truth, label="Truth")
    # transverse_sum = np.mean((spectrum.spectrogram-spectrum.spectrogram_bgd)*spectrum.expo
    # /(parameters.FLAM_TO_ADURATE*spectrum.lambdas*spectrum.lambdas_binwidths), axis=0)
    # transverse_sum *= np.max(spectrum.data)/np.max(transverse_sum)
    # ax[0].plot(spectrum.lambdas, transverse_sum, label="Transverse sum")
    ax[0].set_ylabel(f"Spectrum [{spectrum.units}]")
    ax[0].legend()
    amplitude_truth_interp = interp1d(lambdas_truth, amplitude_truth, kind='cubic', fill_value=0, bounds_error=False)(spectrum.lambdas)
    residuals = (spectrum.data - amplitude_truth_interp)/spectrum.err
    ax[1].errorbar(spectrum.lambdas, residuals, yerr=np.ones_like(spectrum.data), label="Fit", fmt="r.")
    ax[1].set_ylabel(f"Residuals")
    ax[1].set_xlabel(r"$\lambda$ [nm]")
    ax[1].grid()
    ax[1].legend()
    ax[1].text(0.05, 0.05, f'mean={np.mean(residuals):.3g}\nstd={np.std(residuals):.3g}',
               horizontalalignment='left', verticalalignment='bottom',
               color='black', transform=ax[1].transAxes)
    fig.tight_layout()
    fig.subplots_adjust(wspace=0, hspace=0)
    plt.show()
    return residuals


def make_test_image():
    spectrum_filename = "outputs/reduc_20170530_134_spectrum.fits"
    image_filename = spectrum_filename.replace("_spectrum.fits", ".fits")
    ImageSim(image_filename, spectrum_filename, "./tests/data/", A1=A1_T, A2=A2_T,
             psf_poly_params=PSF_POLY_PARAMS_TRUTH, with_stars=True, with_rotation=True)


def fullchain_run(sim_image="./tests/data/sim_20170530_134.fits"):
    # load test and make image simulation
    if not os.path.isfile(sim_image):
        make_test_image()
    image = Image(sim_image)
    lambdas_truth = np.fromstring(image.header['LBDAS_T'][1:-1], sep=' ')
    amplitude_truth = np.fromstring(image.header['AMPLIS_T'][1:-1], sep=' ', dtype=float)
    parameters.AMPLITUDE_TRUTH = np.copy(amplitude_truth)
    parameters.LAMBDA_TRUTH = np.copy(lambdas_truth)

    # extractor
    tag = sim_image.split('/')[-1]
    tag = tag.replace('sim_', 'reduc_')
    logbook = LogBook(logbook="./ctiofulllogbook_jun2017_v5.csv")
    disperser_label, target, xpos, ypos = logbook.search_for_image(tag)
    parameters.CCD_REBIN = 1
    parameters.PSF_POLY_ORDER = PSF_POLY_ORDER
    # spectrum = Spectractor(sim_image, "./tests/data", guess=[xpos, ypos], target_label=target,
    #                        disperser_label=disperser_label)
    #
    # # tests
    # residuals = plot_residuals(spectrum, lambdas_truth, amplitude_truth)
    #
    # spectrum.my_logger.warning(f"\n\tQuantities to test:"
    #                            f"\n\t\tspectrum.header['X0_T']={spectrum.header['X0_T']} vs {spectrum.x0[0]}"
    #                            f"\n\t\tspectrum.header['Y0_T']={spectrum.header['Y0_T']} vs {spectrum.x0[1]}"
    #                            f"\n\t\tspectrum.header['ROT_T']={spectrum.header['ROT_T']} vs {spectrum.rotation_angle}"
    #                            f"\n\t\tspectrum.header['BKGD_LEV']={spectrum.header['BKGD_LEV']} vs {np.mean(spectrum.spectrogram_bgd)}"
    #                            f"\n\t\tspectrum.header['D2CCD_T']={spectrum.header['D2CCD_T']} vs {spectrum.disperser.D}"
    #                            f"\n\t\tspectrum.header['A2_FIT']={spectrum.header['A2_FIT']} vs {A2_T}"
    #                            f"\n\t\tspectrum.header['CHI2_FIT']={spectrum.header['CHI2_FIT']}"
    #                            f"\n\t\tspectrum.chromatic_psf.poly_params={spectrum.chromatic_psf.poly_params[spectrum.chromatic_psf.Nx:]} vs {PSF_POLY_PARAMS_TRUTH}"
    #                            f"\n\t\tresiduals wrt truth: mean={np.mean(residuals[100:-100])}, std={np.std(residuals[100:-100])}")
    # assert np.isclose(float(spectrum.header['X0_T']), spectrum.x0[0], atol=0.05)
    # assert np.isclose(float(spectrum.header['Y0_T']), spectrum.x0[1], atol=0.05)
    # assert np.isclose(float(spectrum.header['ROT_T']), spectrum.rotation_angle,
    #                   atol=180 / np.pi * 1 / parameters.CCD_IMSIZE)
    # assert np.isclose(float(spectrum.header['BKGD_LEV']), np.mean(spectrum.spectrogram_bgd), atol=5e-3)
    # assert np.isclose(float(spectrum.header['D2CCD_T']), spectrum.disperser.D, atol=0.08)
    # assert float(spectrum.header['CHI2_FIT']) < 0.65
    # assert np.all(np.isclose(spectrum.chromatic_psf.poly_params[spectrum.chromatic_psf.Nx+6:], np.array(PSF_POLY_PARAMS_TRUTH)[6:], atol=0.15))
    # assert np.abs(np.mean(residuals[100:-100])) < 0.1
    # assert np.std(residuals[100:-100]) < 1
    spectrum_file_name = "./tests/data/sim_20170530_134_spectrum.fits"
    assert os.path.isfile(spectrum_file_name)
    spectrum = Spectrum(spectrum_file_name)
    atmgrid_filename = sim_image.replace('sim', 'reduc').replace('.fits', '_atmsim.fits')
    assert os.path.isfile(atmgrid_filename)

    w = SpectrumFitWorkspace(spectrum_file_name, atmgrid_file_name=atmgrid_filename, nsteps=1000,
                             burnin=200, nbins=10, verbose=1, plot=True, live_fit=False)
    run_spectrum_minimisation(w, method="newton")
    nsigma = 5
    labels = ["A1_T", "OZONE_T", "PWV_T", "VAOD_T"]
    indices = [0, 2, 3, 4]
    assert w.costs[-1] < 0.58
    for i, l in zip(indices, labels):
        spectrum.my_logger.info(f"\n\tTest {l} best-fit {w.p[i]}+/-{np.sqrt(w.cov[i, i])} vs {spectrum.header[l]}"
                                f" at {nsigma}sigma level: "
                                f"{np.abs(w.p[i]-spectrum.header[l]) / np.sqrt(w.cov[i, i]) < nsigma}")
        assert np.abs(w.p[i]-spectrum.header[l]) / np.sqrt(w.cov[i, i]) < nsigma
    assert np.abs(w.p[1]) / np.sqrt(w.cov[1, 1]) < nsigma  # A2
    assert np.isclose(w.p[6], spectrum.header["D2CCD_T"], atol=parameters.DISTANCE2CCD_ERR)  # D2CCD
    assert np.isclose(np.abs(w.p[7]), 0, atol=parameters.PIXSHIFT_PRIOR)  # pixshift
    assert np.isclose(np.abs(w.p[8]), 0, atol=1e-3)  # B

    parameters.DEBUG = False
    w = SpectrogramFitWorkspace(spectrum_file_name, atmgrid_file_name=atmgrid_filename, nsteps=1000,
                                burnin=2, nbins=10, verbose=1, plot=True, live_fit=False)
    run_spectrogram_minimisation(w, method="newton")
    nsigma = 5
    labels = ["A1_T", "A2_T", "OZONE_T", "PWV_T", "VAOD_T", "D2CCD_T"]
    indices = [0, 1, 2, 3, 4, 5]
    assert w.costs[-1] < 0.68
    for i, l in zip(indices, labels):
        spectrum.my_logger.info(f"\n\tTest {l} best-fit {w.p[i]}+/-{np.sqrt(w.cov[i, i])} vs {spectrum.header[l]}"
                                f" at {nsigma}sigma level: "
                                f"{np.abs(w.p[i]-spectrum.header[l]) / np.sqrt(w.cov[i, i]) < nsigma}")
        assert np.abs(w.p[i]-spectrum.header[l]) / np.sqrt(w.cov[i, i]) < nsigma
    assert np.isclose(np.abs(w.p[8]), 0, atol=parameters.PIXSHIFT_PRIOR)  # shift_y
    assert np.isclose(np.abs(w.p[9]), spectrum.header["ROT_T"], atol=2e-2)  # angle
    assert np.isclose(np.abs(w.p[10]), 1, atol=1e-3)  # B


def test_fullchain():
    parameters.VERBOSE = True
    parameters.DEBUG = True
    sim_image = "./tests/data/sim_20170530_134.fits"
    load_config("./config/ctio.ini")
    fullchain_run(sim_image=sim_image)


if __name__ == "__main__":

    run_module_suite()
