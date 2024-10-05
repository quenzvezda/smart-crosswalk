class DistanceEstimator:
    def __init__(self, focal_length, real_width):
        """
        Inisialisasi DistanceEstimator
        :param focal_length: Panjang fokus kamera (kalibrasi sebelumnya)
        :param real_width: Lebar nyata objek dalam cm
        """
        self.focal_length = focal_length
        self.real_width = real_width

    def estimate(self, pixel_width):
        """
        Menghitung estimasi jarak berdasarkan lebar objek dalam piksel
        :param pixel_width: Lebar bounding box objek dalam piksel
        :return: Estimasi jarak dalam cm
        """
        if pixel_width > 0:
            distance = (self.real_width * self.focal_length) / pixel_width
            return distance
        else:
            return None
